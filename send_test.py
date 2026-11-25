from paho.mqtt.publish import single
import json

sample = {
    "device_id": "test-remote",
    "sequence_num": 0,
    "gesture": "increase",
}

single("ee250/v1/remote/motion", payload=json.dumps(sample), hostname="127.0.0.1")

print("Message sent!")

