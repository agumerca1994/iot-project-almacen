from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    correo = Column(String, unique=True, nullable=False)

    productos = relationship("Producto", back_populates="usuario")
    dispositivos = relationship("Device", back_populates="usuario")


class Producto(Base):
    __tablename__ = "productos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)
    descripcion = Column(String)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))

    usuario = relationship("Usuario", back_populates="productos")
    dispositivo = relationship("Device", back_populates="producto", uselist=False)
    stock = relationship("PantryContent", back_populates="producto", uselist=False)


class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    serial_number = Column(String, unique=True, index=True, nullable=False)
    nombre = Column(String, nullable=True)  # Este será igual al nombre del producto
    estado = Column(String, nullable=False)
    tipo = Column(String, nullable=True)
    firmware_version = Column(String, nullable=True)
    asignado_a_producto = Column(Boolean, default=False)
    fecha_registro = Column(DateTime, default=datetime.utcnow)
    ultima_comunicacion = Column(DateTime, nullable=True)
    comentarios = Column(String, nullable=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=True)

    usuario = relationship("Usuario", back_populates="dispositivos")
    producto = relationship("Producto", back_populates="dispositivo")


class PantryContent(Base):
    __tablename__ = "alacena"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("productos.id"), nullable=False)
    quantity = Column(Integer, nullable=False)

    producto = relationship("Producto", back_populates="stock")
