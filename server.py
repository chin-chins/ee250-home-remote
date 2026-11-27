"""Day-one dashboard and MQTT receiver. AI-assisted starter implementation."""
import argparse
import json
import logging
import math
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import paho.mqtt.client as mqtt

PREFIX = "ee250/v1"
ROOT = Path(__file__).parent
RECORDING_FILE = ROOT / "data" / "recording.jsonl"
lock = threading.Lock()
state = {
    "broker_connected": False, "mode": "music", "volume": 50,
    "playing": False, "brightness": 50, "light_on": False,
    "last_gesture": None, "motion_windows": 0, "last_motion_at": None,
    "last_device": None, "invalid_messages": 0,
    "recording_state": "Waiting for data",
    "recorded_windows": 0,
}


def validate_window(msg):
    if not isinstance(msg, dict) or msg.get("schema_version") != 1:
        raise ValueError("Expected schema_version 1")
    for key in ("device_id", "boot_id"):
        if not isinstance(msg.get(key), str) or not msg[key] or len(msg[key]) > 64:
            raise ValueError(f"Invalid {key}")
    for key in ("seq", "t0_ms"):
        if type(msg.get(key)) is not int or msg[key] < 0:
            raise ValueError(f"Invalid {key}")
    if msg.get("sample_rate_hz") != 50 or msg.get("units") != {"accel": "m/s^2", "gyro": "rad/s"}:
        raise ValueError("Expected 50 Hz and SI units")
    samples = msg.get("samples")
    if not isinstance(samples, list) or len(samples) != 100:
        raise ValueError("Expected exactly 100 samples")
    for row in samples:
        if not isinstance(row, list) or len(row) != 6:
            raise ValueError("Expected six axes per sample")
        if any(type(v) not in (int, float) or not math.isfinite(v) for v in row):
            raise ValueError("Samples must contain finite numbers")


def on_connect(client, userdata, flags, reason_code, properties):
    with lock:
        state["broker_connected"] = not reason_code.is_failure
    if not reason_code.is_failure:
        client.subscribe(f"{PREFIX}/remote/motion", qos=1)


def on_disconnect(client, userdata, flags, reason_code, properties):
    with lock:
        state["broker_connected"] = False


def on_message(client, userdata, message):
    try:
        if len(message.payload) > 65536:
            raise ValueError("Payload too large")
        msg = json.loads(message.payload)
        validate_window(msg)

        with lock:
            state["motion_windows"] += 1
            state["last_motion_at"] = time.time()
            state["last_device"] = msg["device_id"]
        
        try:
            # creates data directory to store motion windows (if it already doesn't exist)
            RECORDING_FILE.parent.mkdir(parents=True, exist_ok=True)

            record = {
                "received_at": time.time(),
                "window": msg,
            }

            # opens file in append mode to save motion window data 
            with RECORDING_FILE.open("a", encoding="utf-8") as file:
                file.write(json.dumps(record) + "\n")

        except OSError:
            logging.exception("Could not save motion window")
            with lock:
                state["recording_state"] = "Save failed"
            return 

        print(f"Received motion window {msg['seq']} from {msg['device_id']}")
        
        with lock:
            state["recording_state"] = "Saved successfully"
            state["recorded_windows"] += 1
            
    except (ValueError, TypeError, KeyError):
        logging.warning("Rejected invalid motion window")
        with lock:
            state["invalid_messages"] += 1


def apply_action(gesture):
    if gesture not in {"switch_mode", "increase", "decrease", "toggle"}:
        raise ValueError("Unknown gesture")
    with lock:
        state["last_gesture"] = gesture
        if gesture == "switch_mode":
            state["mode"] = "light" if state["mode"] == "music" else "music"
        elif gesture == "toggle":
            key = "playing" if state["mode"] == "music" else "light_on"
            state[key] = not state[key]
        else:
            key = "volume" if state["mode"] == "music" else "brightness"
            state[key] = max(0, min(100, state[key] + (10 if gesture == "increase" else -10)))


class Handler(BaseHTTPRequestHandler):
    def respond(self, code, payload, content_type="application/json"):
        body = payload if isinstance(payload, bytes) else json.dumps(payload).encode()
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/":
            self.respond(200, (ROOT / "web" / "index.html").read_bytes(), "text/html; charset=utf-8")
        elif self.path == "/api/state":
            with lock:
                snapshot = dict(state)
            self.respond(200, snapshot)
        else:
            self.respond(404, {"error": "Not found"})

    def do_POST(self):
        if self.path != "/api/action":
            self.respond(404, {"error": "Not found"})
            return
        # This dashboard is local-only; reject cross-site browser requests.
        if self.headers.get("Sec-Fetch-Site") == "cross-site":
            self.respond(403, {"error": "Local requests only"})
            return
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if not 0 < size <= 1024:
                raise ValueError("Invalid body length")
            payload = json.loads(self.rfile.read(size))
            if not isinstance(payload, dict) or not isinstance(payload.get("gesture"), str):
                raise ValueError("Expected a gesture string")
            apply_action(payload["gesture"])
            self.respond(200, {"ok": True})
        except (ValueError, TypeError):
            self.respond(400, {"error": "Expected a valid gesture action"})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mqtt-host", default="127.0.0.1")
    parser.add_argument("--mqtt-port", type=int, default=1883)
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message
    client.reconnect_delay_set(min_delay=1, max_delay=30)
    client.connect_async(args.mqtt_host, args.mqtt_port, 30)
    client.loop_start()
    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print(f"Dashboard: http://127.0.0.1:{args.port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        client.disconnect()
        client.loop_stop()


if __name__ == "__main__":
    main()
