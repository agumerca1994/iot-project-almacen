import json
from notification_models import Notification
from notification_mqtt import publish_mqtt

def log_and_publish_notification(db, topic, payload):
    status = "enviado"
    error_msg = None
    ok, err = publish_mqtt(topic, payload)
    if not ok:
        status = "error"
        error_msg = err
    notif = Notification(
        topic=topic,
        payload=json.dumps(payload),
        status=status,
        error_msg=error_msg
    )
    db.add(notif)
    db.commit()
    return notif
