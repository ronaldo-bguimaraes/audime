from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.v1.schemas import ExtracaoRequest, ExtracaoResponse
from app.core.deps import get_current_user_id, get_db
from app.services.extracao_service import executar_extracao
from abstract.models.core import Extracao

router = APIRouter(prefix="/v1/extracoes", tags=["extracoes"])


@router.post("", response_model=dict, status_code=201)
def criar_extracao(body: ExtracaoRequest, db: Session = Depends(get_db), id_usuario: int = Depends(get_current_user_id)):
    return executar_extracao(body.url, id_usuario, db)


@router.get("/{id_extracao}", response_model=ExtracaoResponse)
def obter_extracao(id_extracao: int, db: Session = Depends(get_db)):
    return db.get(Extracao, id_extracao)
