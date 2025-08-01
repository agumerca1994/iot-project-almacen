# --- IMPORTS Y DEFINICIÓN DE ROUTER ---

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
import crud, schemas
from notification_utils import log_and_publish_notification
from notification_models import Topic

router = APIRouter(prefix="/devices", tags=["devices"])
# --- EDITAR DISPOSITIVO ---
@router.put("/{device_id}", response_model=schemas.Device)
async def editar_dispositivo(device_id: int, data: dict = Body(...), db: Session = Depends(get_db)):
    dispositivo = crud.get_device_by_id(db, device_id)
    if not dispositivo:
        raise HTTPException(status_code=404, detail="Dispositivo no encontrado")
    # Permitir editar producto_id y tipo SIEMPRE que se guarde
    if "producto_id" in data:
        dispositivo.producto_id = data["producto_id"]
    if "tipo" in data:
        dispositivo.tipo = data["tipo"]
    db.commit()
    db.refresh(dispositivo)
    # Notificar al hardware siempre que se edite
    topic_obj = db.query(Topic).filter(Topic.id == 1).first()
    if topic_obj:
        topic_name = topic_obj.nombre
        if "{serial_number}" in topic_name:
            topic_name = topic_name.format(serial_number=dispositivo.serial_number)
        elif topic_name.endswith('-'):
            topic_name = f"{topic_name}{dispositivo.serial_number}"
        payload = {"product_id": dispositivo.producto_id, "estado": dispositivo.estado, "user_id": dispositivo.usuario_id}
        log_and_publish_notification(db, topic_name, payload)
    return dispositivo

# --- DESASIGNAR DISPOSITIVO ---
@router.put("/{device_id}/unassign", response_model=schemas.Device)
async def desasignar_dispositivo(device_id: int, db: Session = Depends(get_db)):
    dispositivo = crud.get_device_by_id(db, device_id)
    if not dispositivo:
        raise HTTPException(status_code=404, detail="Dispositivo no encontrado")
    serial_number_original = dispositivo.serial_number  # Guardar para notificación
    # NO borrar el serial_number, solo desasignar producto y estado
    dispositivo.estado = "desasignado"
    dispositivo.producto_id = None
    dispositivo.asignado_a_producto = False
    db.commit()
    db.refresh(dispositivo)
    # Notificar al hardware usando el serial original
    topic_obj = db.query(Topic).filter(Topic.id == 1).first()
    if topic_obj:
        topic_name = topic_obj.nombre
        if "{serial_number}" in topic_name:
            topic_name = topic_name.format(serial_number=serial_number_original)
        elif topic_name.endswith('-'):
            topic_name = f"{topic_name}{serial_number_original}"
        payload = {"product_id": None, "estado": dispositivo.estado, "user_id": dispositivo.usuario_id}
        log_and_publish_notification(db, topic_name, payload)
    return dispositivo

# --- ELIMINAR DISPOSITIVO ---
@router.delete("/{device_id}")
async def eliminar_dispositivo(device_id: int, db: Session = Depends(get_db)):
    dispositivo = crud.get_device_by_id(db, device_id)
    if not dispositivo:
        raise HTTPException(status_code=404, detail="Dispositivo no encontrado")
    # Notificar al hardware antes de eliminar
    topic_obj = db.query(Topic).filter(Topic.id == 1).first()
    if topic_obj:
        topic_name = topic_obj.nombre
        if "{serial_number}" in topic_name:
            topic_name = topic_name.format(serial_number=dispositivo.serial_number)
        elif topic_name.endswith('-'):
            topic_name = f"{topic_name}{dispositivo.serial_number}"
        payload = {"product_id": None, "estado": dispositivo.estado, "user_id": dispositivo.usuario_id}
        log_and_publish_notification(db, topic_name, payload)
    db.delete(dispositivo)
    db.commit()
    return {"detail": "Dispositivo eliminado"}

# --- COMANDOS (RESET/RESTABLECER) ---
@router.post("/{device_id}/command")
async def comando_dispositivo(device_id: int, command: dict = Body(...), db: Session = Depends(get_db)):
    dispositivo = crud.get_device_by_id(db, device_id)
    if not dispositivo:
        raise HTTPException(status_code=404, detail="Dispositivo no encontrado")
    # Topic de comandos: topic id 2 + serial_number
    topic_obj = db.query(Topic).filter(Topic.id == 2).first()
    if not topic_obj:
        raise HTTPException(status_code=400, detail="No existe topic de comandos id=2")
    topic_name = topic_obj.nombre
    if "{serial_number}" in topic_name:
        topic_name = topic_name.format(serial_number=dispositivo.serial_number)
    elif topic_name.endswith('-'):
        topic_name = f"{topic_name}{dispositivo.serial_number}"
    payload = {"command": command.get("command")}
    log_and_publish_notification(db, topic_name, payload)
    return {"detail": f"Comando {command.get('command')} enviado"}


@router.get("/", response_model=list[schemas.Device])
def listar_dispositivos(
    estado: str | None = Query(default=None),
    tipo: str | None = Query(default=None),
    asignado: bool | None = Query(default=None),
    db: Session = Depends(get_db)
):
    return crud.get_devices(db, estado=estado, tipo=tipo, asignado=asignado)

@router.post("/", response_model=schemas.Device)
async def crear_dispositivo(
    device: schemas.DeviceCreate,
    db: Session = Depends(get_db)
):
    return await crud.create_device(db, device)

@router.get("/{device_id}", response_model=schemas.Device)
def obtener_dispositivo(device_id: int, db: Session = Depends(get_db)):
    dispositivo = crud.get_device_by_id(db, device_id)
    if not dispositivo:
        raise HTTPException(status_code=404, detail="Dispositivo no encontrado")
    return dispositivo
