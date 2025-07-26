from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import schemas, crud
from database import get_db

router = APIRouter(prefix="/global-devices", tags=["global-devices"])

@router.post("/", response_model=schemas.GlobalDevice)
def crear_global_device(device: schemas.GlobalDeviceCreate, db: Session = Depends(get_db)):
    return crud.create_global_device(db, device)

@router.get("/{id_GlobalDevice}", response_model=schemas.GlobalDevice)
def obtener_device_por_id(id_GlobalDevice: int, db: Session = Depends(get_db)):
    device = crud.get_global_device_by_id(db, id_GlobalDevice)
    if not device:
        raise HTTPException(status_code=404, detail="Dispositivo no encontrado")
    return device

@router.get("/serial/{serial_number}", response_model=schemas.GlobalDevice)
def obtener_device_por_serial(serial_number: int, db: Session = Depends(get_db)):
    device = crud.get_global_device_by_serial(db, serial_number)
    if not device:
        raise HTTPException(status_code=404, detail="Dispositivo no encontrado")
    return device

@router.put("/serial/{serial_number}", response_model=schemas.GlobalDevice)
def actualizar_device_por_serial(serial_number: int, data: schemas.GlobalDeviceUpdate, db: Session = Depends(get_db)):
    updated = crud.update_global_device_by_serial(db, serial_number, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Dispositivo no encontrado")
    return updated


@router.delete("/{id_GlobalDevice}")
def eliminar_device(id_GlobalDevice: int, db: Session = Depends(get_db)):
    success = crud.delete_global_device(db, id_GlobalDevice)
    if not success:
        raise HTTPException(status_code=404, detail="Dispositivo no encontrado")
    return {"ok": True}
