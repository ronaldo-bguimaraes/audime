from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from arq.connections import ArqRedis

from app.api.v1.schemas import (
    ExtracaoJobResponse,
    ExtracaoRequest,
    ExtracaoResponse,
    ExtracaoStatusResponse,
)
from app.core.deps import get_current_user_id, get_db
from app.core.deps_arq import get_arq_pool
from abstract.models.core import Extracao, ExtracaoStatus

router = APIRouter(prefix="/v1/extracoes", tags=["extracoes"])


@router.post(
    "",
    response_model=ExtracaoJobResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def criar_extracao(
    body: ExtracaoRequest,
    db: Session = Depends(get_db),
    id_usuario: int = Depends(get_current_user_id),
    arq: ArqRedis = Depends(get_arq_pool),
) -> ExtracaoJobResponse:
    """Enqueue a new NFC-e extraction.

    Creates a ``PENDING`` extraction record, enqueues an ARQ job for
    background processing, and returns immediately with HTTP 202.
    """
    # 1. Create extraction record in PENDING status
    extracao = Extracao(id_usuario=id_usuario, status=ExtracaoStatus.PENDING)
    db.add(extracao)
    db.commit()
    db.refresh(extracao)

    # 2. Enqueue ARQ job (scalar params only — no SQLAlchemy objects)
    job = await arq.enqueue_job(
        "executar_extracao",
        url=body.url,
        id_extracao=extracao.id_extracao,
        id_usuario=id_usuario,
        _job_id=f"extracao:{extracao.id_extracao}",
        _queue="audime:extracoes",
    )

    return ExtracaoJobResponse(
        id_extracao=extracao.id_extracao,
        status=ExtracaoStatus.PENDING.value,
        job_id=job.job_id if job else None,
    )


@router.get(
    "",
    response_model=list[ExtracaoResponse],
)
def listar_extracoes(
    db: Session = Depends(get_db),
    id_usuario: int = Depends(get_current_user_id),
    limit: int = Query(default=10, ge=1, le=100),
) -> list[ExtracaoResponse]:
    """List extractions for the authenticated user, most recent first."""
    extracoes = (
        db.query(Extracao)
        .filter(Extracao.id_usuario == id_usuario)
        .order_by(Extracao.created_at.desc())
        .limit(limit)
        .all()
    )
    return extracoes  # type: ignore[return-value]


@router.get(
    "/{id_extracao}/status",
    response_model=ExtracaoStatusResponse,
)
def obter_status_extracao(
    id_extracao: int,
    db: Session = Depends(get_db),
    id_usuario: int = Depends(get_current_user_id),
) -> ExtracaoStatusResponse:
    """Return the current status of an extraction (polling endpoint)."""
    extracao = db.get(Extracao, id_extracao)
    if extracao is None or extracao.id_usuario != id_usuario:
        raise HTTPException(status_code=404, detail="Extração não encontrada")
    return ExtracaoStatusResponse(
        id_extracao=extracao.id_extracao,
        status=extracao.status.value,
    )


@router.get(
    "/{id_extracao}",
    response_model=ExtracaoResponse,
)
def obter_extracao(
    id_extracao: int,
    db: Session = Depends(get_db),
    id_usuario: int = Depends(get_current_user_id),
) -> ExtracaoResponse | None:
    """Return the full extraction record."""
    extracao = db.get(Extracao, id_extracao)
    if extracao is None or extracao.id_usuario != id_usuario:
        raise HTTPException(status_code=404, detail="Extração não encontrada")
    return extracao  # type: ignore[return-value]
