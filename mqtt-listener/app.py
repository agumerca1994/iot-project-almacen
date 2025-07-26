import json
import time
import requests
import paho.mqtt.client as mqtt

# Configuración del broker MQTT y endpoints
MQTT_BROKER = "emqx"
MQTT_PORT = 1883
MQTT_TOPIC = "iot/lecturas"
MQTT_TOPIC_GLOBAL_DEVICE = "iot/dispositivos"
MQTT_TOPIC_GLOBAL_DEVICE_UPDATE = "iot/global-device-update"
API_BASE_URL = "http://backend:8000"

def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("✅ Conectado al broker MQTT")
        client.subscribe(MQTT_TOPIC)
        print(f"📡 Suscripto al topic {MQTT_TOPIC}")
        client.subscribe(MQTT_TOPIC_GLOBAL_DEVICE)
        print(f"📡 Suscripto al topic {MQTT_TOPIC_GLOBAL_DEVICE}")
        client.subscribe(MQTT_TOPIC_GLOBAL_DEVICE_UPDATE)
        print(f"📡 Suscripto al topic {MQTT_TOPIC_GLOBAL_DEVICE_UPDATE}")
    else:
        print(f"❌ Falló la conexión al broker, código: {rc}")

def on_message(client, userdata, msg):
    try:
        print(f"📥 Mensaje recibido bruto en {msg.topic}: {msg.payload.decode()}")
        payload = json.loads(msg.payload.decode())

        if msg.topic == MQTT_TOPIC:
            product_id = payload.get("product_id")
            measured_value = payload.get("measured_value")

            if not product_id or measured_value is None:
                print("❌ Payload incompleto:", payload)
                return

            print(f"🔄 Actualizando stock → product_id={product_id}, quantity={measured_value}")
            post_payload = {
                "product_id": product_id,
                "quantity": measured_value
            }
            response = requests.post(f"{API_BASE_URL}/alacena", json=post_payload)

            if response.status_code == 200:
                print(f"✅ Stock actualizado correctamente para product_id={product_id}")
            else:
                print(f"❌ Error al actualizar alacena: {response.status_code} - {response.text}")

        elif msg.topic == MQTT_TOPIC_GLOBAL_DEVICE:
            print("🔄 Registrando nuevo dispositivo global...")
            response = requests.post(f"{API_BASE_URL}/global-devices", json=payload)

            if response.status_code == 200:
                print("✅ Dispositivo global registrado correctamente")
            else:
                print(f"❌ Error al registrar global_device: {response.status_code} - {response.text}")
                print("📦 Payload enviado:", payload)

        elif msg.topic == MQTT_TOPIC_GLOBAL_DEVICE_UPDATE:
            print("🔄 Actualizando datos de dispositivo global...")

            serial_number = payload.get("serial_number")
            if not serial_number:
                print("❌ No se especificó serial_number en el mensaje")
                return

            response = requests.put(
                f"{API_BASE_URL}/global-devices/{serial_number}",
                json=payload
            )

            if response.status_code == 200:
                print("✅ Dispositivo global actualizado correctamente")
            else:
                print(f"❌ Error al actualizar global_device: {response.status_code} - {response.text}")
                print("📦 Payload enviado:", payload)

    except Exception as e:
        print("❌ Error procesando mensaje:", e)

def main():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.username_pw_set("admin", "public")
    client.on_connect = on_connect
    client.on_message = on_message

    print("🔌 Conectando al broker...")
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_forever()

if __name__ == "__main__":
    time.sleep(5)  # Espera a que el backend y el broker estén listos
    main()
