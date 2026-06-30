"""Pipeline offline: raw -> staging -> core -> analytics.

Executa em batch para normalizar dados brutos e popular agregações.
"""

from sqlalchemy.orm import Session

from abstract.engine import SessionLocal
from abstract.models.analytics import GastoCategoria, GastoMensal
from abstract.models.raw import ItemNota, Nota, Transacao
from abstract.models.staging import ItemNormalizado, NotaNormalizada


def normalizar_notas(db: Session):
    notas = db.query(Nota).all()
    for nota in notas:
        exists = db.query(NotaNormalizada).filter_by(id_nota=nota.id_nota).first()
        if exists:
            continue
        normalizada = NotaNormalizada(
            id_nota=nota.id_nota,
            id_usuario=nota.id_usuario,
            valor_total=nota.valor_total,
            emitente=nota.empresa,
            data_emissao=nota.emissao,
            chave_acesso=nota.chave,
        )
        db.add(normalizada)
        db.flush()

        for item in nota.items:
            item_norm = ItemNormalizado(
                id_item_nota=item.id_item_nota,
                id_nota_normalizada=normalizada.id_nota_normalizada,
                id_usuario=item.id_usuario,
                descricao=item.item_descricao,
                quantidade=item.item_quantidade,
                valor_unitario=item.item_valor_unidade,
                valor_total=item.item_valor_total,
            )
            db.add(item_norm)

    db.commit()


def atualizar_analytics(db: Session):
    from sqlalchemy import func

    gastos = (
        db.query(
            Transacao.id_usuario,
            func.date_trunc("month", Transacao.data_realizacao).label("mes_ano"),
            func.sum(Transacao.valor).label("total_gasto"),
            func.count(Transacao.id_transacao).label("qtd_transacoes"),
        )
        .group_by(Transacao.id_usuario, "mes_ano")
        .all()
    )

    for g in gastos:
        existing = db.query(GastoMensal).filter_by(
            id_usuario=g.id_usuario, mes_ano=g.mes_ano
        ).first()
        if existing:
            existing.total_gasto = g.total_gasto
            existing.qtd_transacoes = g.qtd_transacoes
        else:
            db.add(GastoMensal(
                id_usuario=g.id_usuario,
                mes_ano=g.mes_ano,
                total_gasto=g.total_gasto,
                qtd_transacoes=g.qtd_transacoes,
            ))

    db.commit()


def run():
    with SessionLocal() as db:
        normalizar_notas(db)
        atualizar_analytics(db)


if __name__ == "__main__":
    run()
