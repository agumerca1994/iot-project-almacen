from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import schemas, crud
from database import get_db

router = APIRouter(prefix="/usuarios", tags=["usuarios"])

@router.get("/", response_model=list[schemas.UsuarioOut])
def listar_usuarios(db: Session = Depends(get_db)):
    return crud.get_usuarios(db)

@router.post("/", response_model=schemas.UsuarioOut)
def crear_usuario(usuario: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    return crud.create_usuario(db, usuario)
