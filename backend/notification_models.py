from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from database import Base

class Notification(Base):
    __tablename__ = "notificaciones"
    id = Column(Integer, primary_key=True, index=True)
    fecha_envio = Column(DateTime(timezone=True), server_default=func.now())
    topic = Column(String, nullable=False)
    payload = Column(Text, nullable=False)
    status = Column(String, nullable=False)
    error_msg = Column(Text, nullable=True)

class Topic(Base):
    __tablename__ = "topics"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, nullable=False)
    descripcion = Column(Text, nullable=True)
