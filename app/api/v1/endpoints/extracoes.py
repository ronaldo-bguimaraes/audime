from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from arq.connections import ArqRedis

from app.api.v1.schemas import (
    BackfillResponse,
    ExtracaoJobResponse,
    ExtracaoRequest,
    ExtracaoResponse,
    ExtracaoStatusResponse,
    ForceResetRequest,
    ForceResetResponse,
    ParsingAttemptItem,
    ParsingAttemptResponse,
    PipelineStepResponse,
    ReprocessarExtracaoRequest,
    ReprocessarExtracaoResponse,
)
from app.core.deps import get_current_user_id, get_db
from app.core.deps_arq import get_arq_pool
from app.services.step_service import init_steps, reset_steps
from abstract.models.analytics import NotaAnalytics
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
    """Enqueue a new NFC-e extraction."""
    extracao = Extracao(
        id_usuario=id_usuario,
        status=ExtracaoStatus.PENDING,
        url=str(body.url),
    )
    db.add(extracao)
    db.commit()
    db.refresh(extracao)

    init_steps(db, extracao.id_extracao)

    job = await arq.enqueue_job(
        "app.workers.tasks.executar_extracao",
        url=str(body.url),
        id_extracao=extracao.id_extracao,
        id_usuario=id_usuario,
        _job_id=f"extracao:{extracao.id_extracao}",
        _queue_name="audime:extracoes",
    )

    return ExtracaoJobResponse(
        id_extracao=extracao.id_extracao,
        status=ExtracaoStatus.PENDING.value,
        job_id=job.job_id if job else None,
    )


def _build_historico_parsing(db: Session, id_extracao: int) -> list[ParsingAttemptResponse]:
    """Build historico of all raw parsing attempts for an extraction."""
    from abstract.models.raw import Importacao, ItemNota, Nota

    importacoes = (
        db.query(Importacao)
        .filter(Importacao.id_extracao == id_extracao)
        .order_by(Importacao.imported_at.desc())
        .limit(10)
        .all()
    )
    result: list[ParsingAttemptResponse] = []
    for imp in importacoes:
        nota = (
            db.query(Nota)
            .filter(Nota.id_importacao == imp.id_importacao)
            .first()
        )
        if nota is None:
            result.append(
                ParsingAttemptResponse(
                    id_importacao=imp.id_importacao,
                    imported_at=imp.imported_at,
                )
            )
            continue
        items_list = [
            ParsingAttemptItem(
                descricao=it.item_descricao,
                quantidade=float(it.item_quantidade) if it.item_quantidade else None,
                unidade=it.item_tipo_unidade,
                valor_total=float(it.item_valor_total) if it.item_valor_total else None,
            )
            for it in nota.items
        ]
        result.append(
            ParsingAttemptResponse(
                id_importacao=imp.id_importacao,
                id_nota=nota.id_nota,
                imported_at=imp.imported_at,
                empresa=nota.empresa,
                chave=nota.chave,
                numero=nota.numero,
                serie=nota.serie,
                emissao=nota.emissao,
                valor_total=float(nota.valor_total) if nota.valor_total else None,
                qtd_total_itens=nota.qtd_total_itens,
                items=items_list,
            )
        )
    return result


def _latest_empresa(db: Session, id_extracao: int) -> str | None:
    """Get the empresa name from the latest successful parsing of an extraction."""
    from abstract.models.raw import Importacao, Nota

    nota = (
        db.query(Nota.empresa)
        .join(Importacao, Importacao.id_importacao == Nota.id_importacao)
        .filter(Importacao.id_extracao == id_extracao)
        .order_by(Importacao.imported_at.desc())
        .first()
    )
    return nota[0] if nota else None


def _build_steps(db: Session, id_extracao: int) -> list[PipelineStepResponse]:
    """Build step list for an extraction."""
    from abstract.models.core import ExtracaoStep

    steps = (
        db.query(ExtracaoStep)
        .filter(ExtracaoStep.id_extracao == id_extracao)
        .order_by(ExtracaoStep.ordem)
        .all()
    )
    return [
        PipelineStepResponse(
            etapa=s.etapa.value,
            status=s.status.value,
            ordem=s.ordem,
            iniciado_em=s.iniciado_em,
            concluido_em=s.concluido_em,
            mensagem=s.mensagem,
        )
        for s in steps
    ]


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
    result = []
    for ext in extracoes:
        result.append(
            ExtracaoResponse(
                id_extracao=ext.id_extracao,
                status=ext.status.value,
                created_at=ext.created_at,
                url=ext.url,
                reprocess_count=ext.reprocess_count,
                reprocessed_at=ext.reprocessed_at,
                historico_parsing=_build_historico_parsing(db, ext.id_extracao),
                steps=_build_steps(db, ext.id_extracao),
                empresa=_latest_empresa(db, ext.id_extracao),
            )
        )
    return result


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
        url=extracao.url,
        reprocess_count=extracao.reprocess_count,
        reprocessed_at=extracao.reprocessed_at,
    )


@router.get(
    "/{id_extracao}",
    response_model=ExtracaoResponse,
)
def obter_extracao(
    id_extracao: int,
    db: Session = Depends(get_db),
    id_usuario: int = Depends(get_current_user_id),
) -> ExtracaoResponse:
    """Return the full extraction record with historico de parsing."""
    extracao = db.get(Extracao, id_extracao)
    if extracao is None or extracao.id_usuario != id_usuario:
        raise HTTPException(status_code=404, detail="Extração não encontrada")
    return ExtracaoResponse(
        id_extracao=extracao.id_extracao,
        status=extracao.status.value,
        created_at=extracao.created_at,
        url=extracao.url,
        reprocess_count=extracao.reprocess_count,
        reprocessed_at=extracao.reprocessed_at,
        historico_parsing=_build_historico_parsing(db, id_extracao),
        steps=_build_steps(db, id_extracao),
        empresa=_latest_empresa(db, id_extracao),
    )


@router.post(
    "/{id_extracao}/reprocessar",
    response_model=ReprocessarExtracaoResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def reprocessar_extracao(
    id_extracao: int,
    body: ReprocessarExtracaoRequest | None = None,
    db: Session = Depends(get_db),
    id_usuario: int = Depends(get_current_user_id),
    arq: ArqRedis = Depends(get_arq_pool),
) -> ReprocessarExtracaoResponse:
    """Reprocess an extraction: re-download, re-parse, create new analytics version.

    Only DONE or ERROR extractions can be reprocessed.
    Optional URL override in request body.
    """
    from sqlalchemy import func, update

    extracao = db.get(Extracao, id_extracao)
    if extracao is None or extracao.id_usuario != id_usuario:
        raise HTTPException(status_code=404, detail="Extração não encontrada")

    if extracao.status in (ExtracaoStatus.PENDING, ExtracaoStatus.RUNNING):
        raise HTTPException(
            status_code=409,
            detail="Extração está em processamento. Aguarde concluir.",
        )

    target_url = str(body.url) if body and body.url else extracao.url
    has_url = bool(target_url)

    # Row lock to prevent concurrent reprocess
    db.execute(
        update(Extracao)
        .where(Extracao.id_extracao == id_extracao)
        .values(
            status=ExtracaoStatus.PENDING,
            reprocess_count=func.coalesce(Extracao.reprocess_count, 0) + 1,
            reprocessed_at=datetime.now(timezone.utc),
        )
    )
    db.commit()

    reset_steps(db, id_extracao)

    if has_url:
        # Full reprocess: re-download, re-parse, re-transform
        job = await arq.enqueue_job(
            "app.workers.tasks.executar_extracao",
            url=target_url,
            id_extracao=id_extracao,
            id_usuario=id_usuario,
            _job_id=f"extracao:{id_extracao}:reprocess:{extracao.reprocess_count or 0}",
            _queue_name="audime:extracoes",
        )
    else:
        # Transform-only: no URL available, just re-run the transform pipeline
        job = await arq.enqueue_job(
            "app.workers.tasks.transformar_extracao",
            id_extracao=id_extracao,
            _queue_name="audime:extracoes",
            _job_id=f"transform:{id_extracao}:reprocess:{extracao.reprocess_count or 0}",
        )

    return ReprocessarExtracaoResponse(
        id_extracao=id_extracao,
        status=ExtracaoStatus.PENDING.value,
        job_id=job.job_id if job else None,
    )


@router.post(
    "/{id_extracao}/force-reset",
    response_model=ForceResetResponse,
    status_code=status.HTTP_200_OK,
)
def force_reset_extracao(
    id_extracao: int,
    body: ForceResetRequest,
    db: Session = Depends(get_db),
    id_usuario: int = Depends(get_current_user_id),
) -> ForceResetResponse:
    """Force-reset a stuck PENDING extraction to ERROR.

    Only PENDING extractions can be force-reset. DONE, RUNNING, and ERROR
    extractions are not considered stuck and return 409.
    """
    extracao = db.get(Extracao, id_extracao)
    if extracao is None or extracao.id_usuario != id_usuario:
        raise HTTPException(status_code=404, detail="Extração não encontrada")

    if extracao.status == ExtracaoStatus.DONE:
        raise HTTPException(
            status_code=409,
            detail="Extração já concluída. Use reprocessar para reprocessar.",
        )
    if extracao.status == ExtracaoStatus.RUNNING:
        raise HTTPException(
            status_code=409,
            detail="Extração em execução. Aguarde concluir.",
        )
    if extracao.status == ExtracaoStatus.ERROR:
        raise HTTPException(
            status_code=409,
            detail="Extração já está em erro. Use reprocessar para tentar novamente.",
        )

    extracao.status = ExtracaoStatus.ERROR
    db.commit()

    return ForceResetResponse(
        id_extracao=id_extracao,
        status=ExtracaoStatus.ERROR.value,
        mensagem=body.mensagem,
    )


@router.post(
    "/backfill",
    response_model=BackfillResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def backfill_transform(
    db: Session = Depends(get_db),
    id_usuario: int = Depends(get_current_user_id),
    arq: ArqRedis = Depends(get_arq_pool),
) -> BackfillResponse:
    """Trigger transform for all DONE extractions without analytics data.

    Enqueues ``transformar_extracao`` for each DONE extraction that has no
    corresponding ``NotaAnalytics`` record. Useful for backfilling after
    a pipeline fix.
    """
    done_extracoes = (
        db.query(Extracao)
        .filter(
            Extracao.id_usuario == id_usuario,
            Extracao.status == ExtracaoStatus.DONE,
        )
        .all()
    )

    # Find which extractions already have analytics
    ids_with_analytics = set()
    if done_extracoes:
        rows = (
            db.query(NotaAnalytics.id_extracao)
            .filter(
                NotaAnalytics.id_extracao.in_([e.id_extracao for e in done_extracoes]),
                NotaAnalytics.id_usuario == id_usuario,
            )
            .distinct()
            .all()
        )
        ids_with_analytics = {r[0] for r in rows}

    enqueued = 0
    for ext in done_extracoes:
        if ext.id_extracao in ids_with_analytics:
            continue
        reset_steps(db, ext.id_extracao)
        await arq.enqueue_job(
            "app.workers.tasks.transformar_extracao",
            id_extracao=ext.id_extracao,
            _queue_name="audime:extracoes",
            _job_id=f"backfill:{ext.id_extracao}",
        )
        enqueued += 1

    return BackfillResponse(
        enqueued=enqueued,
        total=len(done_extracoes),
        message=f"{enqueued} transform jobs enqueued out of {len(done_extracoes)} DONE extractions",
    )
