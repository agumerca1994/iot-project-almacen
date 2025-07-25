from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
import crud
import schemas
from database import get_db

router = APIRouter(prefix="/devices", tags=["devices"])

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
