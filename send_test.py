import json, math, time, uuid
from paho.mqtt.publish import single

samples = []

# server.py takes 100 samples per message
for i in range(100):
    t = i / 50
    wave = math.sin(2 * math.pi * t)

    samples.append([
        round(2.0 * wave, 4), # x accel
        0.0,                  # y accel
        9.81,                 # z accel (gravity)
        0.0,                  # x gyro
        round(0.5 * wave, 4), # y gyro
        0.0,                  # z gyro
    ])

sample = {
    "schema_version": 1,
    "device_id": "test-remote",
    "boot_id": str(uuid.uuid4()),
    "seq": 0,
    "t0_ms": int(time.time() * 1000),
    "sample_rate_hz": 50,
    "units": {"accel": "m/s^2", "gyro": "rad/s"},
    "samples": samples
}

single("ee250/v1/remote/motion", payload=json.dumps(sample), hostname="127.0.0.1", port=1883, qos=1)

print(f"Sent {len(samples)} simulated sensor samples!")

