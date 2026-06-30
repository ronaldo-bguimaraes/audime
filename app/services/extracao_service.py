import posixpath

from sqlalchemy.orm import Session

from app.core.deps import get_current_user_id
from app.services.parser_nfce import parse_nfce
from app.services.storage_service import download_url, generate_filename, hash_sha256, upload_to_r2
from abstract.models.core import Extracao, ExtracaoStatus
from abstract.models.raw import Importacao, ItemNota, Nota

OUTPUT_PREFIX = "imports/html"


def executar_extracao(url: str, db: Session) -> dict:
    id_usuario = get_current_user_id()

    extracao = Extracao(id_usuario=id_usuario, status=ExtracaoStatus.PENDING)
    db.add(extracao)
    db.commit()
    db.refresh(extracao)

    try:
        extracao.status = ExtracaoStatus.RUNNING
        db.commit()

        html_bytes = download_url(url)
        sha256 = hash_sha256(html_bytes)
        filename = generate_filename()
        key = posixpath.join(OUTPUT_PREFIX, filename)

        upload_to_r2(key, html_bytes, {"sha256": sha256})

        importacao = Importacao(
            storage_bucket=posixpath.split(key)[0] or OUTPUT_PREFIX,
            storage_key=key,
            storage_filename=filename,
            sha256=sha256,
            id_extracao=extracao.id_extracao,
            id_usuario=id_usuario,
        )
        db.add(importacao)
        db.commit()
        db.refresh(importacao)

        nota_extraida = parse_nfce(html_bytes)

        nota = Nota(
            empresa=nota_extraida.empresa,
            chave=nota_extraida.chave,
            numero=nota_extraida.numero,
            serie=nota_extraida.serie,
            emissao=nota_extraida.emissao,
            valor_total=nota_extraida.valor_total,
            id_usuario=id_usuario,
            id_importacao=importacao.id_importacao,
        )
        db.add(nota)
        db.commit()
        db.refresh(nota)

        for item_data in nota_extraida.items:
            item = ItemNota(
                item_codigo=item_data["item_codigo"],
                item_descricao=item_data["item_descricao"],
                item_quantidade=item_data["item_quantidade"],
                item_tipo_unidade=item_data["item_tipo_unidade"],
                item_valor_unidade=item_data["item_valor_unidade"],
                item_valor_total=item_data["item_valor_total"],
                id_nota=nota.id_nota,
                id_usuario=id_usuario,
            )
            db.add(item)

        db.commit()

        extracao.status = ExtracaoStatus.DONE
        db.commit()

    except Exception:
        extracao.status = ExtracaoStatus.ERROR
        db.commit()
        raise

    return {
        "id_extracao": extracao.id_extracao,
        "id_nota": nota.id_nota,
    }
