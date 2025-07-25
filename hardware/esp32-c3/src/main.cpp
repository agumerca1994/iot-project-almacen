#include <ESP8266WiFi.h>
#include <WiFiManager.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

WiFiClient espClient;
PubSubClient client(espClient);

// Cambiá esto por la IP local del contenedor EMQX luego
const char* mqtt_server = "192.168.100.119";  
const int mqtt_port = 1883;
const char* mqtt_topic = "iot/lecturas";

unsigned long lastSend = 0;
const unsigned long interval = 15000;  // 15 segundos

void reconnectMQTT() {
  while (!client.connected()) {
    Serial.print("🔌 Intentando conexión MQTT...");
    if (client.connect("ESP8266Client")) {
      Serial.println(" ✅ Conectado");
    } else {
      Serial.print("❌ Error: ");
      Serial.println(client.state());
      delay(5000);
    }
  }
}

void setup() {
  Serial.begin(115200);

  WiFiManager wm;
  if (!wm.autoConnect("ESP8266_Config")) {
    Serial.println("❌ Falló WiFi, reiniciando...");
    ESP.restart();
  }

  Serial.println("✅ Conectado a WiFi.");
  Serial.println(WiFi.localIP());

  client.setServer(mqtt_server, mqtt_port);
}

void loop() {
  if (!client.connected()) {
    reconnectMQTT();
  }
  client.loop();

  unsigned long now = millis();
  if (now - lastSend > interval) {
    lastSend = now;

    int valor = random(0, 1001);  // valor aleatorio entre 0 y 1000
    Serial.print("📦 Enviando: ");
    Serial.println(valor);

    // Crear mensaje JSON
    StaticJsonDocument<128> doc;
    doc["device_id"] = 2;
    doc["product_id"] = 1;
    doc["measured_value"] = valor;

    char payload[128];
    serializeJson(doc, payload);
    client.publish(mqtt_topic, payload);
  }
}
