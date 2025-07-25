#include <ESP8266WiFi.h>        // Conexión WiFi para ESP8266
#include <WiFiManager.h>        // Gestión automática de red WiFi
#include <PubSubClient.h>       // Cliente MQTT
#include <ArduinoJson.h>        // Generación de mensajes JSON

WiFiClient espClient;
PubSubClient client(espClient);

// Configuración del broker MQTT
const char* mqtt_server = "192.168.100.119";
const int mqtt_port = 1883;
const char* mqtt_topic_datos = "iot/lecturas";              // Tópico de datos de medición
const char*   mqtt_topic_registro = "iot/dispositivos"; // Tópico para identificar el dispositivo al conectar

unsigned long lastSend = 0;
const unsigned long interval = 15000;  // 15 segundos

// Función que publica información del dispositivo al broker
void publicarInfoDispositivo() {
  StaticJsonDocument<256> doc;

  String clave = "clave" + String(ESP.getChipId());  // Clave dinámica basada en ChipID

  doc["serial_number"] = ESP.getChipId();
  doc["password"] = clave;
  doc["estado"] = "libre"; // Estado del dispositivo que indica que está libre sin usuario asignado
  doc["firmware_version"] = "v1.0.0";
  doc["uptime_seconds"] = millis() / 1000;
  doc["ip_address"] = WiFi.localIP().toString();
  doc["mac_address"] = WiFi.macAddress();
  doc["wifi_ssid"] = WiFi.SSID();
  doc["rssi"] = WiFi.RSSI();

  char payload[256];
  serializeJson(doc, payload);

  client.publish(mqtt_topic_registro, payload, true);  // Publicar en tópico de registro
  Serial.println("📡 Info de dispositivo enviada al broker:");
  Serial.println(payload);
}

// Función para reconectar al broker MQTT
void reconnectMQTT() {
  while (!client.connected()) {
    Serial.print("🔌 Intentando conexión MQTT...");
    if (client.connect("ESP8266Client")) {
      Serial.println(" ✅ Conectado");

      publicarInfoDispositivo();  // ✅ Enviar info al conectar

    } else {
      Serial.print("❌ Error: ");
      Serial.println(client.state());
      delay(5000);
    }
  }
}

// Setup: se ejecuta una vez al encender
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

// Loop principal: se ejecuta continuamente
void loop() {
  if (!client.connected()) {
    reconnectMQTT();
  }
  client.loop();

  unsigned long now = millis();
  if (now - lastSend > interval) {
    lastSend = now;

    int valor = random(0, 1001);  // Simula una lectura entre 0 y 1000
    Serial.print("📦 Enviando: ");
    Serial.println(valor);

    StaticJsonDocument<128> doc;
    doc["product_id"] = 1;  // Producto fijo por ahora
    doc["measured_value"] = valor;

    char payload[128];
    serializeJson(doc, payload);
    client.publish(mqtt_topic_datos, payload);
  }
}
