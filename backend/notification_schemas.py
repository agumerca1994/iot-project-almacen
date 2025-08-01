from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime

class NotificationCreate(BaseModel):
    topic: str
    payload: Any

class NotificationOut(BaseModel):
    id: int
    fecha_envio: datetime
    topic: str
    payload: Any
    status: str
    error_msg: Optional[str]
    class Config:
        orm_mode = True

class TopicBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None

class TopicCreate(TopicBase):
    pass

class TopicUpdate(BaseModel):
    nombre: Optional[str]
    descripcion: Optional[str]

class TopicOut(TopicBase):
    id: int
    class Config:
        orm_mode = True
