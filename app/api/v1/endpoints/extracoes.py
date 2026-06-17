from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.v1.schemas import ExtracaoRequest, ExtracaoResponse
from app.core.deps import get_db
from app.services.extracao_service import executar_extracao
from database.models.core import Extracao

router = APIRouter(prefix="/v1/extracoes", tags=["extracoes"])


@router.post("", response_model=dict, status_code=201)
def criar_extracao(body: ExtracaoRequest, db: Session = Depends(get_db)):
    return executar_extracao(body.url, db)


@router.get("/{id_extracao}", response_model=ExtracaoResponse)
def obter_extracao(id_extracao: int, db: Session = Depends(get_db)):
    return db.get(Extracao, id_extracao)
