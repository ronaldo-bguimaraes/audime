from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.api.v1.schemas import DashboardNotaItem, DashboardNotaResponse, VersaoNotaResponse
from app.core.deps import get_current_user_id, get_db
from abstract.models.analytics import NotaAnalytics

router = APIRouter(prefix="/v1/dashboard", tags=["dashboard"])


@router.get(
    "/notas",
    response_model=list[DashboardNotaResponse],
)
def listar_notas(
    db: Session = Depends(get_db),
    id_usuario: int = Depends(get_current_user_id),
) -> list[DashboardNotaResponse]:
    """List all current analytics notas for the user."""
    notas = (
        db.query(NotaAnalytics)
        .options(joinedload(NotaAnalytics.items))
        .filter(
            NotaAnalytics.id_usuario == id_usuario,
            NotaAnalytics.is_current == True,  # noqa: E712
        )
        .order_by(NotaAnalytics.valid_from.desc())
        .all()
    )

    result = []
    for n in notas:
        items = [
            DashboardNotaItem(
                descricao=i.descricao or "",
                quantidade=float(i.quantidade) if i.quantidade else None,
                unidade=i.unidade,
                valor_unitario=float(i.valor_unitario) if i.valor_unitario else None,
                valor_total=float(i.valor_total) if i.valor_total else None,
            )
            for i in n.items
        ]
        result.append(
            DashboardNotaResponse(
                id_nota_analytics=n.id_nota_analytics,
                id_extracao=n.id_extracao,
                empresa=n.empresa,
                chave_acesso=n.chave_acesso,
                numero=n.numero,
                serie=n.serie,
                emissao=n.emissao,
                valor_total=float(n.valor_total) if n.valor_total else None,
                qtd_total_itens=n.qtd_total_itens,
                version=n.version,
                valid_from=n.valid_from,
                items=items,
            )
        )

    return result


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
        version=nota.version,
        valid_from=nota.valid_from,
        items=items,
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
            NotaAnalytics.is_current == True,  # noqa: E712
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
    """Return all SCD2 versions of a nota for a given extraction."""
    versoes = (
        db.query(NotaAnalytics)
        .filter(
            NotaAnalytics.id_extracao == id_extracao,
            NotaAnalytics.id_usuario == id_usuario,
        )
        .order_by(NotaAnalytics.version.desc())
        .all()
    )
    if not versoes:
        raise HTTPException(status_code=404, detail="Nenhuma versão encontrada para esta extração")

    return [
        VersaoNotaResponse(
            version=v.version,
            valid_from=v.valid_from,
            valid_to=v.valid_to,
            is_current=v.is_current,
            empresa=v.empresa,
            valor_total=float(v.valor_total) if v.valor_total else None,
        )
        for v in versoes
    ]
