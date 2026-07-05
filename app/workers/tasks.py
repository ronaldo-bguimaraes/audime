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
    """Worker function: download via httpx, upload to R2, parse, append to raw.

    Always INSERTs into raw (append-only). Never UPDATEs or DELETEs raw rows.
    After successful insert, enqueues a transform job for staging analytics.
    """
    from app.services.step_service import set_step_done, set_step_error, set_step_running

    db_factory = ctx["db_session_factory"]
    r2_client = ctx["r2_client"]
    bucket = ctx["bucket"]

    from abstract.models.core import Extracao, ExtracaoStatus, PipelineStep
    from abstract.models.raw import Importacao, ItemNota, Nota

    db = db_factory()
    try:
        extracao = db.get(Extracao, id_extracao)
        if extracao is None:
            raise RuntimeError(f"Extracao {id_extracao} not found")

        extracao.status = ExtracaoStatus.RUNNING
        set_step_running(db, id_extracao, PipelineStep.RAW_IMPORT)
        db.commit()

        # Download via httpx
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            response = await client.get(url)
            response.raise_for_status()
            html_bytes = response.content

        # Hash & filename
        sha256 = hash_sha256(html_bytes)
        filename = generate_filename()
        key = posixpath.join(OUTPUT_PREFIX, filename)

        # Upload to R2
        await asyncio.to_thread(
            r2_client.put_object,
            Body=html_bytes,
            Bucket=bucket,
            Key=key,
            Metadata={"sha256": sha256},
        )

        # Persist import record (append-only)
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

        # Parse HTML
        nota_extraida = await asyncio.to_thread(parse_nfce, html_bytes, url)

        # Fallback: extract chave from URL
        chave = nota_extraida.chave
        if not chave:
            import re
            from urllib.parse import parse_qs, urlparse
            qs = parse_qs(urlparse(str(url)).query)
            p_val = qs.get("p", [None])[0]
            if p_val:
                m = re.match(r"(\d{44})", p_val)
                if m:
                    chave = m.group(1)

        # Parse emission date
        from datetime import datetime

        emissao_date = None
        if nota_extraida.emissao:
            try:
                emissao_date = datetime.strptime(
                    nota_extraida.emissao.split()[0], "%d/%m/%Y"
                ).date()
            except (ValueError, IndexError):
                emissao_date = None

        # INSERT nota (append-only: always new row)
        nota = Nota(
            empresa=nota_extraida.empresa if nota_extraida.empresa else "Desconhecida",
            chave=chave,
            numero=nota_extraida.numero or "0",
            serie=nota_extraida.serie or "0",
            emissao=emissao_date or datetime.now().date(),
            valor_total=nota_extraida.valor_total,
            qtd_total_itens=nota_extraida.qtd_total_itens,
            extra=nota_extraida.extra,
            id_usuario=id_usuario,
            id_importacao=importacao.id_importacao,
        )
        db.add(nota)
        db.commit()
        db.refresh(nota)

        # INSERT items
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

        # Mark RAW_IMPORT as done
        set_step_done(db, id_extracao, PipelineStep.RAW_IMPORT)

        # Mark success
        extracao.status = ExtracaoStatus.DONE
        db.commit()

        # Enqueue transform job (event)
        arq_pool = ctx.get("arq_pool")
        if arq_pool is not None:
            await arq_pool.enqueue_job(
                "app.workers.tasks.transformar_extracao",
                id_extracao=id_extracao,
                _queue_name="audime:extracoes",
            )

        return {
            "id_extracao": extracao.id_extracao,
            "id_nota": nota.id_nota,
        }

    except Exception as exc:
        try:
            extracao = db.get(Extracao, id_extracao)
            if extracao:
                extracao.status = ExtracaoStatus.ERROR
                set_step_error(db, id_extracao, PipelineStep.RAW_IMPORT, str(exc))
                db.commit()
        except Exception:
            pass
        raise

    finally:
        db.close()


async def transformar_extracao(
    ctx: dict,
    *,
    id_extracao: int,
) -> dict:
    """Pipeline: raw → staging → analytics (SCD2).

    Reads the latest raw import for the extraction, normalizes into staging,
    then inserts a new SCD2 version into analytics, closing the previous one.
    """
    from app.services.step_service import set_step_done, set_step_error, set_step_running

    db_factory = ctx["db_session_factory"]

    from datetime import datetime, timezone

    from abstract.models.analytics import ItemNotaAnalytics, NotaAnalytics
    from abstract.models.core import PipelineStep
    from abstract.models.raw import Importacao, ItemNota, Nota
    from abstract.models.staging import ItemNormalizado, NotaNormalizada

    db = db_factory()
    try:
        now = datetime.now(timezone.utc)

        set_step_running(db, id_extracao, PipelineStep.STAGING)

        # Latest raw data for this extraction
        importacao = (
            db.query(Importacao)
            .filter(Importacao.id_extracao == id_extracao)
            .order_by(Importacao.imported_at.desc())
            .first()
        )
        if importacao is None:
            raise RuntimeError(f"No importacao found for extracao {id_extracao}")

        nota_raw = (
            db.query(Nota)
            .filter(Nota.id_importacao == importacao.id_importacao)
            .first()
        )
        if nota_raw is None:
            raise RuntimeError(f"No nota found for importacao {importacao.id_importacao}")

        # Stage: normalizar
        nota_staging = NotaNormalizada(
            id_nota=nota_raw.id_nota,
            id_importacao=importacao.id_importacao,
            id_extracao=id_extracao,
            id_usuario=nota_raw.id_usuario,
            valor_total=nota_raw.valor_total,
            emitente=nota_raw.empresa,
            data_emissao=nota_raw.emissao,
            chave_acesso=nota_raw.chave,
            processado_em=now,
        )
        db.add(nota_staging)
        db.commit()
        db.refresh(nota_staging)

        for item_raw in nota_raw.items:
            item = ItemNormalizado(
                id_nota_normalizada=nota_staging.id_nota_normalizada,
                id_usuario=nota_raw.id_usuario,
                descricao=item_raw.item_descricao,
                quantidade=item_raw.item_quantidade,
                valor_unitario=item_raw.item_valor_unidade,
                valor_total=item_raw.item_valor_total,
                processado_em=now,
            )
            db.add(item)

        db.commit()
        set_step_done(db, id_extracao, PipelineStep.STAGING)
        set_step_running(db, id_extracao, PipelineStep.ANALYTICS)

        # Analytics: SCD2 insert — close current version for this chave+user
        db.query(NotaAnalytics).filter(
            NotaAnalytics.id_usuario == nota_raw.id_usuario,
            NotaAnalytics.chave_acesso == nota_raw.chave,
            NotaAnalytics.is_current == True,  # noqa: E712
        ).update({"valid_to": now, "is_current": False})

        # Insert new current version
        nova_nota = NotaAnalytics(
            id_extracao=id_extracao,
            id_usuario=nota_raw.id_usuario,
            chave_acesso=nota_raw.chave,
            empresa=nota_raw.empresa,
            numero=nota_raw.numero,
            serie=nota_raw.serie,
            emissao=nota_raw.emissao,
            valor_total=nota_raw.valor_total,
            qtd_total_itens=nota_raw.qtd_total_itens,
            extra=nota_raw.extra,
            valid_from=now,
            is_current=True,
            id_importacao=importacao.id_importacao,
            id_nota_raw=nota_raw.id_nota,
            processado_em=now,
        )
        db.add(nova_nota)
        db.commit()
        db.refresh(nova_nota)

        for item_raw in nota_raw.items:
            item = ItemNotaAnalytics(
                id_nota_analytics=nova_nota.id_nota_analytics,
                descricao=item_raw.item_descricao,
                quantidade=item_raw.item_quantidade,
                unidade=item_raw.item_tipo_unidade,
                valor_unitario=item_raw.item_valor_unidade,
                valor_total=item_raw.item_valor_total,
                processado_em=now,
            )
            db.add(item)

        db.commit()

        set_step_done(db, id_extracao, PipelineStep.ANALYTICS)
        set_step_done(db, id_extracao, PipelineStep.COMPLETE)

        return {
            "id_extracao": id_extracao,
            "id_nota_analytics": nova_nota.id_nota_analytics,
        }

    except Exception as exc:
        db.rollback()
        try:
            set_step_error(db, id_extracao, PipelineStep.STAGING, str(exc))
        except Exception:
            pass
        raise

    finally:
        db.close()
