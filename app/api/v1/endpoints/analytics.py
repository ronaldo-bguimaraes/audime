from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.v1.schemas import GastoCategoriaResponse, GastoMensalResponse
from app.core.deps import get_db
from database.models.analytics import GastoCategoria, GastoMensal

router = APIRouter(prefix="/v1/analytics", tags=["analytics"])


@router.get("/gasto-mensal", response_model=list[GastoMensalResponse])
def gasto_mensal(db: Session = Depends(get_db)):
    return db.query(GastoMensal).all()


@router.get("/gasto-categoria", response_model=list[GastoCategoriaResponse])
def gasto_categoria(db: Session = Depends(get_db)):
    return db.query(GastoCategoria).all()
