from fastapi import FastAPI, WebSocket, Depends, HTTPException
from sqlalchemy.orm import Session
from notification_models import Notification, Topic
from notification_schemas import NotificationCreate, NotificationOut, TopicCreate, TopicUpdate, TopicOut
from notification_utils import log_and_publish_notification
import json
from typing import List
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base, get_db
from routes import productos, alacena, devices, usuarios
from websocket_local import websocket_endpoint  # ✅ aseguramos que sea el nombre correcto
from routes import global_devices  # <- importar tu nuevo router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API Almacén IoT",
    description="Sistema de gestión de dispositivos, productos y alacena por usuario",
    version="1.0.0"
)

## Eliminado: DB Setup duplicado, usamos el de database.py

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
app.include_router(global_devices.router)  # <- incluir en FastAPI

# --- Notificaciones ---
@app.post("/notificar-devices", response_model=NotificationOut)
def notificar_devices(noti: NotificationCreate, db: Session = Depends(get_db)):
    notif = log_and_publish_notification(db, noti.topic, noti.payload)
    db.refresh(notif)
    return notif

# --- CRUD Topics ---
@app.post("/topics", response_model=TopicOut)
def create_topic(topic: TopicCreate, db: Session = Depends(get_db)):
    db_topic = Topic(**topic.dict())
    db.add(db_topic)
    db.commit()
    db.refresh(db_topic)
    return db_topic

@app.get("/topics", response_model=List[TopicOut])
def list_topics(db: Session = Depends(get_db)):
    return db.query(Topic).all()

@app.get("/topics/{topic_id}", response_model=TopicOut)
def get_topic(topic_id: int, db: Session = Depends(get_db)):
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    return topic

@app.put("/topics/{topic_id}", response_model=TopicOut)
def update_topic(topic_id: int, topic: TopicUpdate, db: Session = Depends(get_db)):
    db_topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not db_topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    for k, v in topic.dict(exclude_unset=True).items():
        setattr(db_topic, k, v)
    db.commit()
    db.refresh(db_topic)
    return db_topic

@app.delete("/topics/{topic_id}")
def delete_topic(topic_id: int, db: Session = Depends(get_db)):
    db_topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not db_topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    db.delete(db_topic)
    db.commit()
    return {"ok": True}

# --- Sugerencia de topics ---
@app.get("/topics-sugeridos", response_model=List[str])
def sugerir_topics(q: str = "", db: Session = Depends(get_db)):
    topics = db.query(Topic).filter(Topic.nombre.contains(q)).all()
    return [t.nombre for t in topics]

# ✅ Ruta We
# Socket definida correctamente con tipado explícito
@app.websocket("/ws/devices")
async def websocket_devices(websocket: WebSocket):
    await websocket_endpoint(websocket)
