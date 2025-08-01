import paho.mqtt.publish as publish
import json

def publish_mqtt(topic: str, payload: dict):
    try:
        publish.single(
            topic,
            payload=json.dumps(payload),
            hostname="emqx",
            port=1883,
            auth={'username': 'admin', 'password': 'public'}
        )
        return True, None
    except Exception as e:
        return False, str(e)
