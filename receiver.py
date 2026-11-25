import paho.mqtt.client as mqtt
import json
from flask import Flask, jsonify, render_template

app = Flask(__name__)

# global state dict to keep track of received messages, message count, other info 
state = {
    "message_count": 0,
    "last_device": None, 
    "last_gesture": None,
    "mqtt_connected": False,

    "mode": "music",
    "volume": 50,
    "playing": False,
    "brightness": 50,
    "light_on": False,
}

# flask routes 
@app.route("/api/state")
def get_state():
    return jsonify(state)

@app.route("/")
def dashboard():
    return render_template("index.html")

# gesture handling functions 
def apply_gesture(gesture):
    if gesture == "switch_mode":
        if state["mode"] == "music":
            state["mode"] = "light"
        else:
            state["mode"] = "music"

    elif gesture == "increase":
        if state["mode"] == "music":
            state["volume"] = min(state["volume"] + 10, 100)
        else:
            state["brightness"] = min(state["brightness"] + 10, 100)

    elif gesture == "decrease":
        if state["mode"] == "music":
            state["volume"] = max(state["volume"] - 10, 0)
        else:
            state["brightness"] = max(state["brightness"] - 10, 0)

    elif gesture == "toggle":
        if state["mode"] == "music":
            state["playing"] = not state["playing"]
        else:
            state["light_on"] = not state["light_on"]

# mqtt callbacks 
def on_connect(client, userdata, flags, reason_code, properties):
    state["mqtt_connected"] = not reason_code.is_failure

    if state["mqtt_connected"]:
        print("Connected successfully")
        client.subscribe("ee250/v1/remote/motion")
    else:
        print(f"Connection failed: {reason_code}")

def on_disconnect(client, userdata, reason_code, properties):
    state["mqtt_connected"] = False
    print(f"Disconnected from MQTT broker: {reason_code}")

def on_message_print(client, userdata, message):
    try:
        data = json.loads(message.payload.decode())

        state["last_device"] = data["device_id"]
        state["last_gesture"] = data["gesture"]
        state["message_count"] += 1

        apply_gesture(data["gesture"])

        print("Current state:", state)

    except (UnicodeDecodeError, json.JSONDecodeError):
        print("Recieved message that isn't valid JSON or could not be decoded.")

    except (KeyError, TypeError):
        print("Message doesn't have the expected fields.")

    # TODO: uncomment the lines if we want to disconnect after getting a certain number of messages 
    # userdata["message_count"] += 1
    # if userdata["message_count"] >= 5:
    #     client.disconnect()

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_message = on_message_print

client.connect("127.0.0.1", 1883, 60)

client.loop_start()
app.run(host="127.0.0.1", port=8000, debug=False)