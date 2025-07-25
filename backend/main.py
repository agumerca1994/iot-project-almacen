from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routes import productos, alacena, devices, usuarios
from websocket_local import websocket_endpoint  # ✅ aseguramos que sea el nombre correcto

# Crear todas las tablas si no existen
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API Almacén IoT",
    description="Sistema de gestión de dispositivos, productos y alacena por usuario",
    version="1.0.0"
)

# Configurar CORS
origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(usuarios.router)
app.include_router(productos.router)
app.include_router(devices.router)
app.include_router(alacena.router)

# ✅ Ruta WebSocket definida correctamente con tipado explícito
@app.websocket("/ws/devices")
async def websocket_devices(websocket: WebSocket):
    await websocket_endpoint(websocket)
