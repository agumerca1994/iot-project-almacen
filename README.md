# 📦 Proyecto IoT - Control de Almacén con ESP8266, MQTT, FastAPI y React

Este proyecto permite conectar dispositivos físicos (ESP8266) para medir stock de productos en una "alacena inteligente". Los valores de stock se actualizan automáticamente mediante MQTT, se almacenan en una base de datos PostgreSQL y se visualizan en un panel web en tiempo real.

---

## 🧱 Componentes del proyecto

- **ESP8266 NodeMCU (CH340G)**  
  Dispositivo IoT que mide stock y publica datos periódicamente.

- **Broker MQTT (EMQX)**  
  Se encarga de recibir los datos desde los dispositivos.

- **MQTT Listener (Python)**  
  Lee los datos publicados y los envía al backend.

- **Backend (FastAPI)**  
  Expone endpoints REST para productos, dispositivos y alacena.

- **Base de Datos (PostgreSQL)**  
  Almacena la información de usuarios, productos, dispositivos y stock.

- **Frontend (React)**  
  Muestra el estado actual de la alacena con WebSockets.

---

## 🚀 Cómo levantar el proyecto

### 1. Clonar el repositorio

```bash
git clone https://github.com/tuusuario/iot-project-almacen.git
cd iot-project-almacen

### 2. Iniciar servicios con Docker

docker-compose up --build

sistema levanta:

    EMQX: http://localhost:18083
        
        _CREDENCIALES EMQX_
        Usuario: admin
        Contraseña: public

    Backend (API): http://localhost:8000
    Frontend (panel): http://localhost:3000

### 3. Como conectar el dispositivo ESP8266

El ESP8266 usa WiFiManager para conectarse a WiFi.
Cada 15 segundos publica datos simulados en el topic: iot/lecturas
Formato del payload:
{
  "device_id": 2,
  "product_id": 1,
  "measured_value": 777
}
Este valor será enviado automáticamente por el mqtt-listener al endpoint:
POST /alacena para actualizar el stock del producto correspondiente.

🧠 Endpoints clave del backend
GET /devices/ → listar dispositivos
GET /devices/{device_id} → obtener info de un dispositivo
POST /alacena → actualizar stock
GET /alacena → ver el contenido actual


Estructura del proyecto

iot-project-almacen/
│
├── backend/              # FastAPI + PostgreSQL
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   ├── routes/
│   ├── websocket_local.py
│   └── ...
│
├── frontend/             # React app (panel web)
│
├── mqtt-listener/        # Python app que escucha al broker MQTT
│   ├── app.py
│   └── requirements.txt
│
├── docker-compose.yml    # Levanta todos los servicios
└── README.md             # Este archivo



