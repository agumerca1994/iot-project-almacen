#include <ESP8266WiFi.h>
#include <WiFiManager.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

WiFiClient espClient;
PubSubClient client(espClient);

const char* mqtt_server = "192.168.100.119";
const int mqtt_port = 1883;
const char* mqtt_topic_datos = "iot/lecturas";
const char* mqtt_topic_registro = "iot-dispositivos";

unsigned long lastSend = 0;
const unsigned long interval = 15000;

String serial;
String estado = "libre";
int product_id = -1;               // Valor inválido por defecto
String user_assignament = "";      // Nuevo: sin usuario asignado

// ======================== CALLBACK MQTT ========================
void callback(char* topic, byte* payload, unsigned int length) {
  String mensaje;
  for (unsigned int i = 0; i < length; i++) {
    mensaje += (char)payload[i];
  }

  Serial.print("📩 Mensaje en ");
  Serial.print(topic);
  Serial.print(": ");
  Serial.println(mensaje);

  String topicComando = "iot/comandos-" + serial;
  String topicDatos = "iot/recepcion-datos-" + serial;

  if (String(topic) == topicComando) {
    if (mensaje == "reset_wifi") {
      Serial.println("🔁 Reset solo WiFi...");
      WiFiManager wm;
      wm.resetSettings();
      delay(1000);
      ESP.restart();
    } else if (mensaje == "reset_all") {
      Serial.println("🔁 Reset total: WiFi + Product ID...");
      WiFiManager wm;
      wm.resetSettings();
      product_id = -1;
      user_assignament = "";
      delay(1000);
      ESP.restart();
    }
  }

  if (String(topic) == topicDatos) {
    StaticJsonDocument<256> doc;
    DeserializationError error = deserializeJson(doc, mensaje);
    if (!error) {
      if (doc.containsKey("product_id")) {
        product_id = doc["product_id"];
        Serial.print("🆕 product_id actualizado: ");
        Serial.println(product_id);
      }
      if (doc.containsKey("estado")) {
        estado = doc["estado"].as<String>();
        Serial.print("🆕 estado actualizado: ");
        Serial.println(estado);
      }
      if (doc.containsKey("user_id")) {
        user_assignament = doc["user_id"].as<String>();
        Serial.print("🧑 user_id asignado: ");
        Serial.println(user_assignament);
      }
    } else {
      Serial.println("❌ Error al parsear JSON");
    }
  }
}

// ======================== PUBLICAR INFO DISPOSITIVO ========================
void publicarInfoDispositivo() {
  StaticJsonDocument<256> doc;

  String password = "clave" + serial;

  doc["serial_number"] = serial;
  doc["password"] = password;
  doc["estado"] = estado;
  doc["firmware_version"] = "v1.0.0";
  doc["uptime_seconds"] = millis() / 1000;
  doc["ip_address"] = WiFi.localIP().toString();
  doc["mac_address"] = WiFi.macAddress();
  doc["wifi_ssid"] = WiFi.SSID();
  doc["rssi"] = WiFi.RSSI();
  doc["user_assignament"] = user_assignament;

  char payload[256];
  serializeJson(doc, payload);

  client.publish(mqtt_topic_registro, payload, true);
  Serial.println("📡 Info de dispositivo enviada:");
  Serial.println(payload);
}

// ======================== RECONNECT MQTT ========================
void reconnectMQTT() {
  while (!client.connected()) {
    Serial.print("🔌 Intentando conexión MQTT...");
    if (client.connect("ESP8266Client")) {
      Serial.println(" ✅ Conectado");

      String topicComando = "iot/comandos-" + serial;
      client.subscribe(topicComando.c_str());
      Serial.print("📡 Suscripto a: ");
      Serial.println(topicComando);

      String topicDatos = "iot/recepcion-datos-" + serial;
      client.subscribe(topicDatos.c_str());
      Serial.print("📡 Suscripto a: ");
      Serial.println(topicDatos);

      publicarInfoDispositivo();

    } else {
      Serial.print("❌ Error: ");
      Serial.println(client.state());
      delay(5000);
    }
  }
}

// ======================== SETUP ========================
void setup() {
  Serial.begin(115200);

  serial = String(ESP.getChipId());
  String password = "clave" + serial;

  WiFiManager wm;

  String html_sn = "<p><strong>Serial Number:</strong> " + serial + "</p>";
  String html_pw = "<p><strong>Password:</strong> " + password + "</p>";
  String html_estado = "<p><strong>Estado:</strong> " + estado + "</p>";
  String html_user = "<p><strong>User ID:</strong> " + user_assignament + "</p>";

  WiFiManagerParameter info_sn(html_sn.c_str());
  WiFiManagerParameter info_pw(html_pw.c_str());
  WiFiManagerParameter info_estado(html_estado.c_str());
  WiFiManagerParameter info_user(html_user.c_str());

  wm.addParameter(&info_sn);
  wm.addParameter(&info_pw);
  wm.addParameter(&info_estado);
  wm.addParameter(&info_user);

  if (!wm.autoConnect("ESP8266_Config")) {
    Serial.println("❌ Falló WiFi, reiniciando...");
    ESP.restart();
  }

  Serial.println("✅ Conectado a WiFi.");
  Serial.println(WiFi.localIP());

  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);
}

// ======================== LOOP ========================
void loop() {
  if (!client.connected()) {
    reconnectMQTT();
  }
  client.loop();

  unsigned long now = millis();
  if (now - lastSend > interval) {
    lastSend = now;

    if (product_id == -1) {
      Serial.println("⚠️ product_id no asignado. No se envía medición.");
      return;
    }

    int valor = random(0, 1001);
    Serial.print("📦 Enviando medición: ");
    Serial.println(valor);

    StaticJsonDocument<128> doc;
    doc["product_id"] = product_id;
    doc["measured_value"] = valor;

    char payload[128];
    serializeJson(doc, payload);
    client.publish(mqtt_topic_datos, payload);
  }
}
