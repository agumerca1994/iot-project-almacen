from sqlalchemy.orm import Session
from models import Usuario, Producto, Device, PantryContent, GlobalDevice
import schemas
from datetime import datetime
from websocket_local import notify_new_device  # ✅ asegúrate que el path sea correcto
from websocket_local import notify_stock_update  # ✅ nuevo import
import models

# ---------------------- USUARIOS ----------------------

def get_usuarios(db: Session):
    return db.query(Usuario).all()

def create_usuario(db: Session, usuario: schemas.UsuarioCreate):
    db_usuario = Usuario(**usuario.dict())
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    return db_usuario


# ---------------------- PRODUCTOS ----------------------

def get_productos(db: Session, usuario_id: int = None):
    query = db.query(models.Producto)
    if usuario_id:
        query = query.filter(models.Producto.usuario_id == usuario_id)
    return query.all()


def create_producto(db: Session, producto: schemas.ProductoCreate):
    db_producto = Producto(**producto.dict())
    db.add(db_producto)
    db.commit()
    db.refresh(db_producto)
    return db_producto


# ---------------------- DISPOSITIVOS ----------------------

def get_devices(db: Session, estado=None, tipo=None, asignado=None):
    query = db.query(Device)
    if estado is not None:
        query = query.filter(Device.estado == estado)
    if tipo is not None:
        query = query.filter(Device.tipo == tipo)
    if asignado is not None:
        query = query.filter(Device.asignado_a_producto == asignado)
    return query.all()

def get_device_by_id(db: Session, device_id: int):
    return db.query(Device).filter(Device.id == device_id).first()


async def create_device(db: Session, device: schemas.DeviceCreate):
    db_device = Device(**device.dict())

    # Buscar el nombre del producto si hay producto_id
    if device.producto_id:
        producto = db.query(models.Producto).filter(models.Producto.id == device.producto_id).first()
        if producto:
            db_device.nombre = producto.nombre

    db.add(db_device)
    db.commit()
    db.refresh(db_device)

    # 🔔 Notificar a los clientes WebSocket
    await notify_new_device({
        "id": db_device.id,
        "nombre": db_device.nombre,
        "serial_number": db_device.serial_number,
        "estado": db_device.estado,
        "asignado_a_producto": db_device.asignado_a_producto,
        "producto_id": db_device.producto_id,
        "usuario_id": db_device.usuario_id,
        "fecha_registro": db_device.fecha_registro.isoformat()
    })

    return db_device

# ---------------------- DISPOSITIVOS GLOBALES ----------------------
def create_global_device(db: Session, device: schemas.GlobalDeviceCreate):
    db_device = GlobalDevice(**device.dict())
    db.add(db_device)
    db.commit()
    db.refresh(db_device)
    return db_device

def get_global_device_by_id(db: Session, id_GlobalDevice: int):
    return db.query(GlobalDevice).filter(GlobalDevice.id_GlobalDevice == id_GlobalDevice).first()

def get_global_device_by_serial(db: Session, serial: int):
    return db.query(GlobalDevice).filter(GlobalDevice.serial_number == serial).first()

def delete_global_device(db: Session, id_GlobalDevice: int):
    device = get_global_device_by_id(db, id_GlobalDevice)
    if device:
        db.delete(device)
        db.commit()
        return True
    return False

def update_global_device_by_serial(db: Session, serial_number: int, data: schemas.GlobalDeviceUpdate):
    device = get_global_device_by_serial(db, serial_number)
    if device:
        for field, value in data.dict().items():
            setattr(device, field, value)
        db.commit()
        db.refresh(device)
        return device
    return None




# ---------------------- ALACENA / STOCK ----------------------

def get_alacena(db: Session):
    return db.query(PantryContent).all()



async def create_alacena(db: Session, item: schemas.PantryContentCreate):
    db_item = PantryContent(product_id=item.product_id, quantity=item.quantity)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)

    # 🔔 Notificar a los clientes
    await notify_stock_update({
        "product_id": db_item.product_id,
        "quantity": db_item.quantity
    })




    return db_item

