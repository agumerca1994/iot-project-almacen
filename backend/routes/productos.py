from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
import schemas, crud
from database import get_db

router = APIRouter(prefix="/productos", tags=["productos"])

@router.get("/", response_model=list[schemas.Producto])
def listar_productos(
    usuario_id: int = Query(None),
    db: Session = Depends(get_db)
):
    return crud.get_productos(db, usuario_id=usuario_id)

@router.post("/", response_model=schemas.Producto)
def crear_producto(
    producto: schemas.ProductoCreate,
    db: Session = Depends(get_db)
):
    return crud.create_producto(db, producto)
