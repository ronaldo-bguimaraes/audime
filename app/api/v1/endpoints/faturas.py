from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.api.v1.schemas import FaturaRequest, FaturaResponse, TransacaoResponse
from app.core.deps import get_db
from abstract.models.raw import Fatura, Transacao

router = APIRouter(prefix="/v1/faturas", tags=["faturas"])


@router.get("", response_model=list[FaturaResponse])
def listar_faturas(db: Session = Depends(get_db)):
    return db.query(Fatura).all()


@router.get("/{id_fatura}", response_model=FaturaResponse)
def obter_fatura(id_fatura: int, db: Session = Depends(get_db)):
    fatura = db.get(Fatura, id_fatura)
    if not fatura:
        raise HTTPException(status_code=404)
    return fatura


@router.get("/{id_fatura}/transacoes", response_model=list[TransacaoResponse])
def listar_transacoes_da_fatura(id_fatura: int, db: Session = Depends(get_db)):
    return db.query(Transacao).filter(Transacao.id_fatura == id_fatura).all()


@router.post("", response_model=FaturaResponse, status_code=201)
def criar_fatura(body: FaturaRequest, db: Session = Depends(get_db)):
    fatura = Fatura(banco=body.banco, nome_titular=body.nome_titular)
    db.add(fatura)
    db.commit()
    db.refresh(fatura)
    return fatura
