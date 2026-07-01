from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.api.v1.schemas import ItemResponse, NotaResponse, VincularFaturaRequest
from app.core.deps import get_current_user_id, get_db
from abstract.models.raw import ItemNota, Nota

router = APIRouter(prefix="/v1/notas", tags=["notas"])


@router.get("", response_model=list[NotaResponse])
def listar_notas(
    db: Session = Depends(get_db),
    id_usuario: int = Depends(get_current_user_id),
):
    return (
        db.query(Nota)
        .options(joinedload(Nota.items))
        .filter(Nota.id_usuario == id_usuario)
        .all()
    )


@router.get("/{id_nota}", response_model=NotaResponse)
def obter_nota(
    id_nota: int,
    db: Session = Depends(get_db),
    id_usuario: int = Depends(get_current_user_id),
):
    nota = (
        db.query(Nota)
        .options(joinedload(Nota.items))
        .filter(Nota.id_nota == id_nota, Nota.id_usuario == id_usuario)
        .first()
    )
    if not nota:
        raise HTTPException(status_code=404)
    return nota


@router.get("/{id_nota}/itens", response_model=list[ItemResponse])
def listar_itens_nota(id_nota: int, db: Session = Depends(get_db)):
    return db.query(ItemNota).filter(ItemNota.id_nota == id_nota).all()


@router.patch("/{id_nota}/vincular-fatura")
def vincular_fatura(id_nota: int, body: VincularFaturaRequest, db: Session = Depends(get_db)):
    nota = db.get(Nota, id_nota)
    if not nota:
        raise HTTPException(status_code=404)
    nota.id_fatura = body.id_fatura
    db.commit()
    return {"status": "vinculado"}
