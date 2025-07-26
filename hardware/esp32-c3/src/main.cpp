#include <ESP8266WiFi.h>
#include <WiFiManager.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

WiFiClient espClient;
PubSubClient client(espClient);

const char* mqtt_server = "192.168.100.119";
const int mqtt_port = 1883;
const char* mqtt_topic_datos = "iot/lecturas";
const char* mqtt_topic_registro = "iot/dispositivos";
const char* mqtt_topic_actualizacion = "iot/global-device-update";

unsigned long lastSend = 0;
const unsigned long interval = 15000;

String serial;
String estado = "libre";
int product_id = -1;
int user_assig = -1;

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
      user_assig = -1;
      delay(1000);
      ESP.restart();
    }
  }

  if (String(topic) == topicDatos) {
    StaticJsonDocument<256> doc;
    DeserializationError error = deserializeJson(doc, mensaje);
    if (!error) {
      bool actualizado = false;

      if (doc.containsKey("product_id")) {
        product_id = doc["product_id"];
        Serial.print("🆕 product_id actualizado: ");
        Serial.println(product_id);
        actualizado = true;
      }
      if (doc.containsKey("estado")) {
        estado = doc["estado"].as<String>();
        Serial.print("🆕 estado actualizado: ");
        Serial.println(estado);
        actualizado = true;
      }
      if (doc.containsKey("user_id")) {
        user_assig = doc["user_id"];
        Serial.print("🧑 user_id asignado: ");
        Serial.println(user_assig);
        actualizado = true;
      }

      if (actualizado) {
        StaticJsonDocument<512> docOut;
        String password = "clave" + serial;

        docOut["sn"] = serial;
        docOut["password"] = password;
        docOut["estado"] = estado;
        docOut["vfirmware"] = "v1.0.0";
        docOut["uptime"] = millis() / 1000;
        docOut["ipadd"] = WiFi.localIP().toString();
        docOut["macadd"] = WiFi.macAddress();
        docOut["ssid"] = WiFi.SSID();
        docOut["rssi"] = WiFi.RSSI();

        if (user_assig != -1) {
          docOut["user_id"] = String(user_assig);  // Se envía como string para evitar error
        }

        char outPayload[512];
        serializeJson(docOut, outPayload);

        Serial.print("📤 Enviando actualización a ");
        Serial.println(mqtt_topic_actualizacion);
        bool ok = client.publish(mqtt_topic_actualizacion, outPayload);
        Serial.println(ok ? "✅ Actualización publicada" : "❌ Error publicando actualización");
        serializeJsonPretty(docOut, Serial);
      }
    } else {
      Serial.println("❌ Error al parsear JSON");
    }
  }
}

// ======================== PUBLICAR INFO DISPOSITIVO ========================
void publicarInfoDispositivo() {
  StaticJsonDocument<512> doc;

  String password = "clave" + serial;

  doc["sn"] = serial;
  doc["password"] = password;
  doc["estado"] = estado;
  doc["vfirmware"] = "v1.0.0";
  doc["uptime"] = millis() / 1000;
  doc["ipadd"] = WiFi.localIP().toString();
  doc["macadd"] = WiFi.macAddress();
  doc["ssid"] = WiFi.SSID();
  doc["rssi"] = WiFi.RSSI();

  if (user_assig != -1) {
    doc["user_id"] = String(user_assig);  // también como string aquí
  }

  char payload[512];
  serializeJson(doc, payload);

  Serial.print("📏 Longitud JSON registro: ");
  Serial.println(strlen(payload));
  bool ok = client.publish(mqtt_topic_registro, payload, true);
  Serial.println(ok ? "✅ Registro publicado" : "❌ Error publicando registro");
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
  String html_user = "<p><strong>User ID:</strong> " + (user_assig == -1 ? "-" : String(user_assig)) + "</p>";

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
