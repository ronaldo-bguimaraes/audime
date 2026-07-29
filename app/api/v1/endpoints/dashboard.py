from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func as sa_func, extract
from sqlalchemy.orm import Session, joinedload

from app.api.v1.schemas import (
    DashboardNotaItem,
    DashboardNotaResponse,
    DashboardResumoResponse,
    EmpresaResumoItem,
    MesResumoItem,
    NotaPatchRequest,
    VersaoNotaResponse,
)
from app.core.deps import get_current_user_id, get_db
from abstract.models.analytics import NotaAnalytics

router = APIRouter(prefix="/v1/dashboard", tags=["dashboard"])


@router.get(
    "/resumo",
    response_model=DashboardResumoResponse,
)
def resumo_dashboard(
    db: Session = Depends(get_db),
    id_usuario: int = Depends(get_current_user_id),
) -> DashboardResumoResponse:
    """Return aggregated financial summary for the dashboard.

    Computes totals, monthly breakdown, and per-company breakdown
    from active NotaAnalytics rows.
    """
    # Base query: active, current notas with non-null chave
    base = db.query(NotaAnalytics).filter(
        NotaAnalytics.id_usuario == id_usuario,
        NotaAnalytics.valid_to.is_(None),
        NotaAnalytics.is_active == True,  # noqa: E712
        NotaAnalytics.chave_acesso.isnot(None),
    )

    # ── Totals ──
    total_notas = base.count()
    valor_total_row = (
        db.query(sa_func.sum(NotaAnalytics.valor_total))
        .filter(
            NotaAnalytics.id_usuario == id_usuario,
            NotaAnalytics.valid_to.is_(None),
            NotaAnalytics.is_active == True,  # noqa: E712
            NotaAnalytics.chave_acesso.isnot(None),
        )
        .scalar()
    )
    valor_total = float(valor_total_row) if valor_total_row else 0.0
    media_por_nota = round(valor_total / total_notas, 2) if total_notas > 0 else None

    ultima = (
        base.order_by(NotaAnalytics.valid_from.desc()).first()
    )
    ultima_extracao = ultima.valid_from if ultima else None

    # ── Monthly breakdown ──
    mes_rows = (
        db.query(
            extract("month", NotaAnalytics.emissao).label("mes"),
            extract("year", NotaAnalytics.emissao).label("ano"),
            sa_func.sum(NotaAnalytics.valor_total).label("valor"),
            sa_func.count(NotaAnalytics.id_nota_analytics).label("quantidade"),
        )
        .filter(
            NotaAnalytics.id_usuario == id_usuario,
            NotaAnalytics.valid_to.is_(None),
            NotaAnalytics.is_active == True,  # noqa: E712
            NotaAnalytics.chave_acesso.isnot(None),
            NotaAnalytics.emissao.isnot(None),
        )
        .group_by("mes", "ano")
        .order_by("ano", "mes")
        .all()
    )
    por_mes = [
        MesResumoItem(
            mes=int(r.mes),
            ano=int(r.ano),
            valor=float(r.valor) if r.valor else 0.0,
            quantidade=int(r.quantidade),
        )
        for r in mes_rows
    ]

    # ── Per-company breakdown ──
    empresa_rows = (
        db.query(
            NotaAnalytics.empresa,
            sa_func.sum(NotaAnalytics.valor_total).label("valor"),
            sa_func.count(NotaAnalytics.id_nota_analytics).label("quantidade"),
        )
        .filter(
            NotaAnalytics.id_usuario == id_usuario,
            NotaAnalytics.valid_to.is_(None),
            NotaAnalytics.is_active == True,  # noqa: E712
            NotaAnalytics.chave_acesso.isnot(None),
            NotaAnalytics.empresa.isnot(None),
        )
        .group_by(NotaAnalytics.empresa)
        .order_by(sa_func.sum(NotaAnalytics.valor_total).desc())
        .all()
    )
    por_empresa = [
        EmpresaResumoItem(
            empresa=r.empresa or "Desconhecida",
            valor=float(r.valor) if r.valor else 0.0,
            quantidade=int(r.quantidade),
        )
        for r in empresa_rows
    ]

    return DashboardResumoResponse(
        total_notas=total_notas,
        valor_total=valor_total,
        media_por_nota=media_por_nota,
        ultima_extracao=ultima_extracao,
        por_mes=por_mes,
        por_empresa=por_empresa,
    )


@router.get(
    "/notas",
    response_model=list[DashboardNotaResponse],
)
def listar_notas(
    db: Session = Depends(get_db),
    id_usuario: int = Depends(get_current_user_id),
) -> list[DashboardNotaResponse]:
    """List the latest current analytics nota per chave_acesso for the user.

    If the same nota (same chave_acesso) was extracted multiple times,
    only the most recent version (highest valid_from) is returned.
    """
    # Latest id_nota_analytics per chave_acesso (non-null chave only)
    latest = (
        db.query(
            sa_func.max(NotaAnalytics.id_nota_analytics).label("max_id"),
        )
        .filter(
            NotaAnalytics.id_usuario == id_usuario,
            NotaAnalytics.valid_to.is_(None),
            NotaAnalytics.is_active == True,  # noqa: E712
            NotaAnalytics.chave_acesso.isnot(None),
        )
        .group_by(NotaAnalytics.chave_acesso)
        .subquery()
    )

    notas = (
        db.query(NotaAnalytics)
        .options(joinedload(NotaAnalytics.items))
        .join(latest, NotaAnalytics.id_nota_analytics == latest.c.max_id)
        .order_by(NotaAnalytics.valid_from.desc())
        .all()
    )

    return [_build_from_analytics(n) for n in notas]


def _build_from_analytics(nota: NotaAnalytics) -> DashboardNotaResponse:
    items = [
        DashboardNotaItem(
            descricao=i.descricao or "",
            quantidade=float(i.quantidade) if i.quantidade else None,
            unidade=i.unidade,
            valor_unitario=float(i.valor_unitario) if i.valor_unitario else None,
            valor_total=float(i.valor_total) if i.valor_total else None,
        )
        for i in nota.items
    ]
    return DashboardNotaResponse(
        id_nota_analytics=nota.id_nota_analytics,
        id_extracao=nota.id_extracao,
        empresa=nota.empresa,
        chave_acesso=nota.chave_acesso,
        numero=nota.numero,
        serie=nota.serie,
        emissao=nota.emissao,
        valor_total=float(nota.valor_total) if nota.valor_total else None,
        qtd_total_itens=nota.qtd_total_itens,
        valid_from=nota.valid_from,
        items=items,
        is_active=nota.is_active,
    )


@router.get(
    "/notas/{id_extracao}",
    response_model=DashboardNotaResponse,
)
def obter_nota(
    id_extracao: int,
    db: Session = Depends(get_db),
    id_usuario: int = Depends(get_current_user_id),
) -> DashboardNotaResponse:
    """Return the current analytics version of a nota for a given extraction."""
    nota = (
        db.query(NotaAnalytics)
        .options(joinedload(NotaAnalytics.items))
        .filter(
            NotaAnalytics.id_extracao == id_extracao,
            NotaAnalytics.id_usuario == id_usuario,
            NotaAnalytics.valid_to.is_(None),
            NotaAnalytics.is_active == True,  # noqa: E712
        )
        .first()
    )
    if not nota:
        raise HTTPException(status_code=404, detail="Nota não encontrada")

    return _build_from_analytics(nota)


@router.get(
    "/notas/{id_extracao}/historico",
    response_model=list[VersaoNotaResponse],
)
def historico_nota(
    id_extracao: int,
    db: Session = Depends(get_db),
    id_usuario: int = Depends(get_current_user_id),
) -> list[VersaoNotaResponse]:
    """Return all SCD2 versions of a nota for the chave associated with this extraction."""
    extra = (
        db.query(NotaAnalytics.chave_acesso)
        .filter(
            NotaAnalytics.id_extracao == id_extracao,
            NotaAnalytics.id_usuario == id_usuario,
        )
        .first()
    )
    if not extra:
        raise HTTPException(status_code=404, detail="Extração não encontrada")

    chave = extra.chave_acesso
    versoes = (
        db.query(NotaAnalytics)
        .filter(
            NotaAnalytics.chave_acesso == chave,
            NotaAnalytics.id_usuario == id_usuario,
        )
        .order_by(NotaAnalytics.valid_from.desc())
        .all()
    )
    if not versoes:
        raise HTTPException(status_code=404, detail="Nenhuma versão encontrada para esta extração")

    return [
        VersaoNotaResponse(
            valid_from=v.valid_from,
            valid_to=v.valid_to,
                is_current=v.valid_to is None,
            empresa=v.empresa,
            valor_total=float(v.valor_total) if v.valor_total else None,
        )
        for v in versoes
    ]


@router.patch("/notas/{id_extracao}")
def patch_nota(
    id_extracao: int,
    body: NotaPatchRequest,
    db: Session = Depends(get_db),
    id_usuario: int = Depends(get_current_user_id),
) -> dict:
    """Toggle is_active (soft-delete / reactivate) for all versions of a nota.

    Sets is_active on ALL SCD2 rows for the given id_extracao and user.
    Returns 404 if no rows exist for this extraction and user.
    """
    rows = (
        db.query(NotaAnalytics)
        .filter(
            NotaAnalytics.id_extracao == id_extracao,
            NotaAnalytics.id_usuario == id_usuario,
        )
        .all()
    )
    if not rows:
        raise HTTPException(status_code=404, detail="Nota não encontrada")

    for row in rows:
        row.is_active = body.is_active
    db.commit()

    return {"status": "ativado" if body.is_active else "desativado"}
