from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# ---------- USUARIOS ----------
class UsuarioBase(BaseModel):
    nombre: str
    correo: str

class UsuarioCreate(UsuarioBase):
    pass

class UsuarioOut(UsuarioBase):
    id: int

    class Config:
        from_attributes = True


# ---------- PRODUCTOS ----------
class ProductoBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None

class ProductoCreate(ProductoBase):
    usuario_id: int

class Producto(ProductoBase):
    id: int
    usuario_id: int

    class Config:
        from_attributes = True


# ---------- DEVICES ----------
class DeviceBase(BaseModel):
    serial_number: str
    nombre: str  # ← Campo nuevo
    estado: str
    tipo: Optional[str] = None
    firmware_version: Optional[str] = None
    asignado_a_producto: Optional[bool] = False
    comentarios: Optional[str] = None

class DeviceCreate(DeviceBase):
    producto_id: Optional[int] = None
    usuario_id: int

class Device(DeviceBase):
    id: int
    fecha_registro: datetime
    ultima_comunicacion: Optional[datetime] = None
    usuario_id: int
    producto_id: Optional[int]

    class Config:
        from_attributes = True


# ---------- ALACENA ----------
class PantryContentBase(BaseModel):
    product_id: int
    quantity: int

class PantryContentCreate(PantryContentBase):
    pass

class PantryContent(PantryContentBase):
    id: int

    class Config:
        from_attributes = True
