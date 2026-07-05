"""Task functions executed by the ARQ worker."""

import asyncio
import posixpath

import httpx

from app.services.parser_nfce import parse_nfce
from app.services.storage_service import generate_filename, hash_sha256

OUTPUT_PREFIX = "imports/html"


async def executar_extracao(
    ctx: dict,
    *,
    url: str,
    id_extracao: int,
    id_usuario: int,
) -> dict:
    """Worker function: download via httpx, upload to R2, parse, persist.

    Parameters
    ----------
    ctx :
        ARQ context — contains ``db_session_factory`` and ``r2_client``.
    url :
        Public URL of the NFC-e HTML.
    id_extracao :
        Primary key of the ``Extracao`` row (must already exist with
        status ``PENDING``).
    id_usuario :
        ID of the user that initiated the extraction.

    Returns
    -------
    dict
        Summary of what was created.

    Notes
    -----
    *   Only scalar parameters are passed — no SQLAlchemy model instances.
    *   The job is idempotent: ``(Nota.chave, Nota.id_usuario)`` is UNIQUE.
    *   Synchronous calls (boto3 ``put_object``, ``parse_nfce``) are
        offloaded via ``asyncio.to_thread`` so they don't block the
        worker's event loop.
    """
    db_factory = ctx["db_session_factory"]
    r2_client = ctx["r2_client"]
    bucket = ctx["bucket"]

    # Import models here to avoid circular imports at module level
    from abstract.models.core import Extracao, ExtracaoStatus
    from abstract.models.raw import Importacao, ItemNota, Nota

    db = db_factory()
    try:
        # ── Look up the extraction row ──────────────────────────────
        extracao = db.get(Extracao, id_extracao)
        if extracao is None:
            raise RuntimeError(f"Extracao {id_extracao} not found")

        extracao.status = ExtracaoStatus.RUNNING
        db.commit()

        # ── Download via httpx (native async) ───────────────────────
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            html_bytes = response.content

        # ── Hash & filename ─────────────────────────────────────────
        sha256 = hash_sha256(html_bytes)
        filename = generate_filename()
        key = posixpath.join(OUTPUT_PREFIX, filename)

        # ── Upload to R2 (sync boto3 → thread) ──────────────────────
        await asyncio.to_thread(
            r2_client.put_object,
            Body=html_bytes,
            Bucket=bucket,
            Key=key,
            Metadata={"sha256": sha256},
        )

        # ── Persist import record ───────────────────────────────────
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

        # ── Parse HTML (sync → thread) ──────────────────────────────
        nota_extraida = await asyncio.to_thread(parse_nfce, html_bytes, url)

        # ── Parse emission date ─────────────────────────────────────
        emissao_date = None
        if nota_extraida.emissao:
            from datetime import datetime

            try:
                emissao_date = datetime.strptime(
                    nota_extraida.emissao.split()[0], "%d/%m/%Y"
                ).date()
            except (ValueError, IndexError):
                emissao_date = None

        # ── Persist nota ────────────────────────────────────────────
        nota = Nota(
            empresa=nota_extraida.empresa,
            chave=nota_extraida.chave,
            numero=nota_extraida.numero,
            serie=nota_extraida.serie,
            emissao=emissao_date,
            valor_total=nota_extraida.valor_total,
            qtd_total_itens=nota_extraida.qtd_total_itens,
            extra=nota_extraida.extra,
            id_usuario=id_usuario,
            id_importacao=importacao.id_importacao,
        )
        db.add(nota)
        db.commit()
        db.refresh(nota)

        # ── Persist items ───────────────────────────────────────────
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

        # ── Mark success ────────────────────────────────────────────
        extracao.status = ExtracaoStatus.DONE
        db.commit()

        return {
            "id_extracao": extracao.id_extracao,
            "id_nota": nota.id_nota,
        }

    except Exception:
        # Mark as ERROR so the status is visible even before retries
        try:
            extracao = db.get(Extracao, id_extracao)
            if extracao:
                extracao.status = ExtracaoStatus.ERROR
                db.commit()
        except Exception:
            pass  # best-effort — don't mask original exception
        raise

    finally:
        db.close()
