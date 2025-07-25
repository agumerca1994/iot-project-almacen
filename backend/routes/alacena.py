from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import schemas, crud
from database import get_db

router = APIRouter(prefix="/alacena", tags=["alacena"])

@router.get("/", response_model=list[schemas.PantryContent])
def listar_alacena(db: Session = Depends(get_db)):
    return crud.get_alacena(db)

@router.post("/", response_model=schemas.PantryContent)
async def agregar_stock(
    item: schemas.PantryContentCreate,
    db: Session = Depends(get_db)
):
    return await crud.create_alacena(db, item)
