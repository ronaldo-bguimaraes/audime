"""Tests for dashboard endpoints — raw fallback and backfill."""

from datetime import datetime, timezone

import sqlalchemy as sa

from abstract.models.core import Extracao, ExtracaoStatus
from abstract.models.raw import Importacao, ItemNota, Nota
from abstract.models.analytics import NotaAnalytics, ItemNotaAnalytics


def _create_extracao_com_nota(db_session, id_extracao=1, id_usuario=1, status=ExtracaoStatus.DONE):
    now = datetime.now(timezone.utc)
    e = Extracao(
        id_extracao=id_extracao,
        id_usuario=id_usuario,
        status=status,
        created_at=now,
        url="https://example.com/nfce",
    )
    db_session.add(e)
    db_session.commit()

    imp = Importacao(
        id_importacao=id_extracao,
        storage_bucket="test",
        storage_key=f"test/{id_extracao}",
        storage_filename=f"file{id_extracao}.html",
        sha256="0" * 64,
        imported_at=now,
        id_extracao=id_extracao,
        id_usuario=id_usuario,
    )
    db_session.add(imp)
    db_session.commit()

    nota = Nota(
        id_nota=id_extracao,
        empresa="Test Empresa",
        chave="31200611222233300014455555555555555555555555",
        numero="123456",
        serie="1",
        emissao=now.date(),
        valor_total=100.50,
        qtd_total_itens=2,
        extra={},
        imported_at=now,
        id_usuario=id_usuario,
        id_importacao=imp.id_importacao,
    )
    db_session.add(nota)
    db_session.commit()

    for i in range(2):
        item = ItemNota(
            id_item_nota=id_extracao * 100 + i,
            item_codigo=str(i),
            item_descricao=f"Item {i}",
            item_quantidade=i + 1,
            item_tipo_unidade="UN",
            item_valor_unidade=10.0,
            item_valor_total=10.0 * (i + 1),
            id_nota=nota.id_nota,
            id_usuario=id_usuario,
        )
        db_session.add(item)
    db_session.commit()

    return e, imp, nota


# ── Tests for raw fallback in list endpoint ──────────────────────────


class TestDashboardListFallback:

    def test_listar_notas_with_analytics(self, client, auth_header, db_session):
        headers, uid = auth_header()
        now = datetime.now(timezone.utc)

        _create_extracao_com_nota(db_session, id_extracao=1, id_usuario=uid)

        nota_analytics = NotaAnalytics(
            id_nota_analytics=1,
            id_extracao=1,
            id_usuario=uid,
            chave_acesso="31200611222233300014455555555555555555555555",
            empresa="Analytics Empresa",
            numero="123456",
            serie="1",
            emissao=now.date(),
            valor_total=200.75,
            qtd_total_itens=3,
            valid_from=now,
            id_importacao=1,
            id_nota_raw=1,
            processado_em=now,
        )
        db_session.add(nota_analytics)
        db_session.commit()

        item = ItemNotaAnalytics(
            id_item_analytics=1,
            id_nota_analytics=1,
            descricao="Item Analytics",
            quantidade=1.0,
            unidade="UN",
            valor_unitario=200.75,
            valor_total=200.75,
            processado_em=now,
        )
        db_session.add(item)
        db_session.commit()

        r = client.get("/v1/dashboard/notas", headers=headers)
        assert r.status_code == 200
        data = r.json()
        assert len(data) == 1
        assert data[0]["id_nota_analytics"] == 1
        assert data[0]["empresa"] == "Analytics Empresa"
        assert data[0]["valor_total"] == 200.75
        assert "version" not in data[0]

    def test_listar_notas_raw_only_returns_empty(self, client, auth_header, db_session):
        headers, uid = auth_header()
        _create_extracao_com_nota(db_session, id_extracao=1, id_usuario=uid)

        r = client.get("/v1/dashboard/notas", headers=headers)
        assert r.status_code == 200
        assert r.json() == []

    def test_listar_notas_no_data_returns_empty_list(self, client, auth_header, db_session):
        headers, _ = auth_header()

        r = client.get("/v1/dashboard/notas", headers=headers)
        assert r.status_code == 200
        assert r.json() == []

    def test_listar_notas_mixed_data(self, client, auth_header, db_session):
        headers, uid = auth_header()
        now = datetime.now(timezone.utc)

        _create_extracao_com_nota(db_session, id_extracao=1, id_usuario=uid)
        _create_extracao_com_nota(db_session, id_extracao=2, id_usuario=uid)

        nota_analytics = NotaAnalytics(
            id_nota_analytics=2,
            id_extracao=2,
            id_usuario=uid,
            chave_acesso="31200611222233300014455555555555555555555555",
            empresa="Analytics Empresa",
            numero="123456",
            serie="1",
            emissao=now.date(),
            valor_total=200.75,
            qtd_total_itens=3,
            valid_from=now,
            id_importacao=2,
            id_nota_raw=2,
            processado_em=now,
        )
        db_session.add(nota_analytics)
        db_session.commit()

        r = client.get("/v1/dashboard/notas", headers=headers)
        assert r.status_code == 200
        data = r.json()
        assert len(data) == 1
        assert data[0]["id_extracao"] == 2

    def test_listar_notas_only_own_user(self, client, auth_header, db_session):
        headers1, uid1 = auth_header(email="user1@test.com")
        headers2, uid2 = auth_header(email="user2@test.com")
        now = datetime.now(timezone.utc)

        _create_extracao_com_nota(db_session, id_extracao=1, id_usuario=uid1)

        nota_analytics = NotaAnalytics(
            id_nota_analytics=1, id_extracao=1, id_usuario=uid1,
            chave_acesso="x", empresa="User1 Only",
            numero="1", serie="1", emissao=now.date(),
            valor_total=100, qtd_total_itens=1,
            valid_from=now,
            id_importacao=1, id_nota_raw=1, processado_em=now,
        )
        db_session.add(nota_analytics)
        db_session.commit()

        r1 = client.get("/v1/dashboard/notas", headers=headers1)
        assert r1.status_code == 200
        assert len(r1.json()) == 1

        r2 = client.get("/v1/dashboard/notas", headers=headers2)
        assert r2.status_code == 200
        assert r2.json() == []

    def test_obter_nota_individual_only_analytics(self, client, auth_header, db_session):
        headers, uid = auth_header()
        now = datetime.now(timezone.utc)
        _create_extracao_com_nota(db_session, id_extracao=1, id_usuario=uid)

        r = client.get("/v1/dashboard/notas/1", headers=headers)
        assert r.status_code == 404

        nota_analytics = NotaAnalytics(
            id_nota_analytics=1, id_extracao=1, id_usuario=uid,
            chave_acesso="x", empresa="Analytics Only",
            numero="1", serie="1", emissao=now.date(),
            valor_total=999.99, qtd_total_itens=1,
            valid_from=now,
            id_importacao=1, id_nota_raw=1, processado_em=now,
        )
        db_session.add(nota_analytics)
        db_session.commit()

        r = client.get("/v1/dashboard/notas/1", headers=headers)
        assert r.status_code == 200
        data = r.json()
        assert data["empresa"] == "Analytics Only"
        assert data["valor_total"] == 999.99

    def test_obter_nota_individual_not_found(self, client, auth_header, db_session):
        headers, _ = auth_header()

        r = client.get("/v1/dashboard/notas/999", headers=headers)
        assert r.status_code == 404


# ── Tests for backfill and reprocess url=None ────────────────────────


class TestDashboardBackfill:

    def test_backfill_endpoint_exists(self, client, auth_header, db_session):
        headers, _ = auth_header()
        r = client.post("/v1/extracoes/backfill", headers=headers)
        assert r.status_code == 202
        data = r.json()
        assert "enqueued" in data
        assert isinstance(data["enqueued"], int)


# ── Tests for soft-delete (is_active) ─────────────────────────────────


class TestSoftDelete:

    def test_is_active_column_exists_on_model(self, client, auth_header, db_session):
        assert "is_active" in NotaAnalytics.__table__.columns
        col = NotaAnalytics.__table__.columns["is_active"]
        assert isinstance(col.type, sa.Boolean)

    def test_is_active_defaults_to_true(self, client, auth_header, db_session):
        _, uid = auth_header()
        now = datetime.now(timezone.utc)
        nota = NotaAnalytics(
            id_nota_analytics=1,
            id_extracao=1,
            id_usuario=uid,
            chave_acesso="31200611222233300014455555555555555555555555",
            empresa="Test Empresa",
            numero="123456",
            serie="1",
            emissao=now.date(),
            valor_total=100.00,
            qtd_total_itens=1,
            valid_from=now,
            id_importacao=1,
            id_nota_raw=1,
            processado_em=now,
        )
        db_session.add(nota)
        db_session.commit()
        assert nota.is_active is True

    def test_listar_notas_filters_inactive(self, client, auth_header, db_session):
        headers, uid = auth_header()
        now = datetime.now(timezone.utc)

        _create_extracao_com_nota(db_session, id_extracao=1, id_usuario=uid)
        _create_extracao_com_nota(db_session, id_extracao=2, id_usuario=uid)

        nota_active = NotaAnalytics(
            id_nota_analytics=1, id_extracao=1, id_usuario=uid,
            chave_acesso="31200611222233300014455555555555555555555555",
            empresa="Active Empresa", numero="123456", serie="1",
            emissao=now.date(), valor_total=100.00, qtd_total_itens=1,
            valid_from=now,
            id_importacao=1, id_nota_raw=1, processado_em=now,
            is_active=True,
        )
        db_session.add(nota_active)

        nota_inactive = NotaAnalytics(
            id_nota_analytics=2, id_extracao=2, id_usuario=uid,
            chave_acesso="21200611222233300014455555555555555555555555",
            empresa="Inactive Empresa", numero="654321", serie="2",
            emissao=now.date(), valor_total=200.00, qtd_total_itens=2,
            valid_from=now,
            id_importacao=2, id_nota_raw=2, processado_em=now,
            is_active=False,
        )
        db_session.add(nota_inactive)
        db_session.commit()

        r = client.get("/v1/dashboard/notas", headers=headers)
        assert r.status_code == 200
        data = r.json()
        assert len(data) == 1
        assert data[0]["empresa"] == "Active Empresa"
        assert data[0]["id_extracao"] == 1

    def test_obter_nota_inactive_returns_404(self, client, auth_header, db_session):
        headers, uid = auth_header()
        now = datetime.now(timezone.utc)

        _create_extracao_com_nota(db_session, id_extracao=1, id_usuario=uid)

        nota = NotaAnalytics(
            id_nota_analytics=1, id_extracao=1, id_usuario=uid,
            chave_acesso="31200611222233300014455555555555555555555555",
            empresa="Test", numero="123456", serie="1",
            emissao=now.date(), valor_total=100.00, qtd_total_itens=1,
            valid_from=now,
            id_importacao=1, id_nota_raw=1, processado_em=now,
            is_active=False,
        )
        db_session.add(nota)
        db_session.commit()

        r = client.get("/v1/dashboard/notas/1", headers=headers)
        assert r.status_code == 404

    def test_obter_nota_active_returns_200(self, client, auth_header, db_session):
        headers, uid = auth_header()
        now = datetime.now(timezone.utc)

        _create_extracao_com_nota(db_session, id_extracao=1, id_usuario=uid)

        nota = NotaAnalytics(
            id_nota_analytics=1, id_extracao=1, id_usuario=uid,
            chave_acesso="31200611222233300014455555555555555555555555",
            empresa="Active Empresa", numero="123456", serie="1",
            emissao=now.date(), valor_total=100.00, qtd_total_itens=1,
            valid_from=now,
            id_importacao=1, id_nota_raw=1, processado_em=now,
            is_active=True,
        )
        db_session.add(nota)
        db_session.commit()

        r = client.get("/v1/dashboard/notas/1", headers=headers)
        assert r.status_code == 200
        assert r.json()["empresa"] == "Active Empresa"

    def test_historico_nota_shows_inactive(self, client, auth_header, db_session):
        headers, uid = auth_header()
        now = datetime.now(timezone.utc)

        _create_extracao_com_nota(db_session, id_extracao=1, id_usuario=uid)

        nota = NotaAnalytics(
            id_nota_analytics=1, id_extracao=1, id_usuario=uid,
            chave_acesso="31200611222233300014455555555555555555555555",
            empresa="Test Empresa", numero="123456", serie="1",
            emissao=now.date(), valor_total=100.00, qtd_total_itens=1,
            valid_from=now,
            id_importacao=1, id_nota_raw=1, processado_em=now,
            is_active=False,
        )
        db_session.add(nota)
        db_session.commit()

        r = client.get("/v1/dashboard/notas/1/historico", headers=headers)
        assert r.status_code == 200
        data = r.json()
        assert len(data) >= 1

    def test_patch_desativar_sets_is_active_false(self, client, auth_header, db_session):
        headers, uid = auth_header()
        now = datetime.now(timezone.utc)

        _create_extracao_com_nota(db_session, id_extracao=1, id_usuario=uid)

        nota = NotaAnalytics(
            id_nota_analytics=1, id_extracao=1, id_usuario=uid,
            chave_acesso="31200611222233300014455555555555555555555555",
            empresa="Test Empresa", numero="123456", serie="1",
            emissao=now.date(), valor_total=100.00, qtd_total_itens=1,
            valid_from=now,
            id_importacao=1, id_nota_raw=1, processado_em=now,
            is_active=True,
        )
        db_session.add(nota)
        db_session.commit()

        r = client.patch(
            "/v1/dashboard/notas/1",
            json={"is_active": False},
            headers=headers,
        )
        assert r.status_code == 200

        db_session.refresh(nota)
        assert nota.is_active is False

    def test_patch_reativar_sets_is_active_true(self, client, auth_header, db_session):
        headers, uid = auth_header()
        now = datetime.now(timezone.utc)

        _create_extracao_com_nota(db_session, id_extracao=1, id_usuario=uid)

        nota = NotaAnalytics(
            id_nota_analytics=1, id_extracao=1, id_usuario=uid,
            chave_acesso="31200611222233300014455555555555555555555555",
            empresa="Test Empresa", numero="123456", serie="1",
            emissao=now.date(), valor_total=100.00, qtd_total_itens=1,
            valid_from=now,
            id_importacao=1, id_nota_raw=1, processado_em=now,
            is_active=False,
        )
        db_session.add(nota)
        db_session.commit()

        r = client.patch(
            "/v1/dashboard/notas/1",
            json={"is_active": True},
            headers=headers,
        )
        assert r.status_code == 200

        db_session.refresh(nota)
        assert nota.is_active is True

    def test_patch_idempotent(self, client, auth_header, db_session):
        headers, uid = auth_header()
        now = datetime.now(timezone.utc)

        _create_extracao_com_nota(db_session, id_extracao=1, id_usuario=uid)

        nota = NotaAnalytics(
            id_nota_analytics=1, id_extracao=1, id_usuario=uid,
            chave_acesso="31200611222233300014455555555555555555555555",
            empresa="Test Empresa", numero="123456", serie="1",
            emissao=now.date(), valor_total=100.00, qtd_total_itens=1,
            valid_from=now,
            id_importacao=1, id_nota_raw=1, processado_em=now,
            is_active=True,
        )
        db_session.add(nota)
        db_session.commit()

        r1 = client.patch(
            "/v1/dashboard/notas/1",
            json={"is_active": False},
            headers=headers,
        )
        assert r1.status_code == 200

        r2 = client.patch(
            "/v1/dashboard/notas/1",
            json={"is_active": False},
            headers=headers,
        )
        assert r2.status_code == 200

    def test_patch_wrong_user_returns_404(self, client, auth_header, db_session):
        headers1, uid1 = auth_header(email="user1@test.com")
        headers2, uid2 = auth_header(email="user2@test.com")
        now = datetime.now(timezone.utc)

        _create_extracao_com_nota(db_session, id_extracao=1, id_usuario=uid1)

        nota = NotaAnalytics(
            id_nota_analytics=1, id_extracao=1, id_usuario=uid1,
            chave_acesso="31200611222233300014455555555555555555555555",
            empresa="Test Empresa", numero="123456", serie="1",
            emissao=now.date(), valor_total=100.00, qtd_total_itens=1,
            valid_from=now,
            id_importacao=1, id_nota_raw=1, processado_em=now,
            is_active=True,
        )
        db_session.add(nota)
        db_session.commit()

        r = client.patch(
            "/v1/dashboard/notas/1",
            json={"is_active": False},
            headers=headers2,
        )
        assert r.status_code == 404

    def test_patch_nonexistent_returns_404(self, client, auth_header, db_session):
        headers, _ = auth_header()

        r = client.patch(
            "/v1/dashboard/notas/999",
            json={"is_active": False},
            headers=headers,
        )
        assert r.status_code == 404


# ── Tests for Dashboard Resumo (Issue #4) ────────────────────────────


class TestDashboardResumo:

    def _seed_user_notas(self, db_session, uid):
        """Helper to seed 3 notas with varied dates and values."""
        from datetime import timedelta
        now = datetime.now(timezone.utc)
        notas_data = [
            dict(id_nota_analytics=1, id_extracao=1, empresa="Loja A",
                 chave_acesso="11111111111111111111111111111111111111111111",
                 emissao=now.date(), valor_total=100.00, qtd_total_itens=1),
            dict(id_nota_analytics=2, id_extracao=2, empresa="Loja B",
                 chave_acesso="22222222222222222222222222222222222222222222",
                 emissao=now.date() - timedelta(days=30), valor_total=200.00, qtd_total_itens=2),
            dict(id_nota_analytics=3, id_extracao=3, empresa="Loja A",
                 chave_acesso="33333333333333333333333333333333333333333333",
                 emissao=now.date() - timedelta(days=60), valor_total=300.00, qtd_total_itens=3),
        ]
        for nd in notas_data:
            db_session.add(NotaAnalytics(
                id_usuario=uid,
                valid_from=now,
                id_importacao=nd["id_extracao"],
                id_nota_raw=nd["id_extracao"],
                processado_em=now,
                **nd,
            ))
        db_session.commit()

    def test_resumo_basic(self, client, auth_header, db_session):
        headers, uid = auth_header()
        self._seed_user_notas(db_session, uid)

        r = client.get("/v1/dashboard/resumo", headers=headers)
        assert r.status_code == 200
        data = r.json()

        assert data["total_notas"] == 3
        assert data["valor_total"] == 600.00
        assert data["media_por_nota"] == 200.0
        assert data["ultima_extracao"] is not None

    def test_resumo_por_mes(self, client, auth_header, db_session):
        headers, uid = auth_header()
        self._seed_user_notas(db_session, uid)

        r = client.get("/v1/dashboard/resumo", headers=headers)
        data = r.json()
        assert len(data["por_mes"]) >= 1
        for item in data["por_mes"]:
            assert "mes" in item
            assert "ano" in item
            assert "valor" in item
            assert "quantidade" in item

    def test_resumo_por_empresa(self, client, auth_header, db_session):
        headers, uid = auth_header()
        self._seed_user_notas(db_session, uid)

        r = client.get("/v1/dashboard/resumo", headers=headers)
        data = r.json()
        # Loja A has 2 notas (100+300), Loja B has 1 (200)
        assert len(data["por_empresa"]) == 2
        loja_a = [e for e in data["por_empresa"] if e["empresa"] == "Loja A"][0]
        assert loja_a["quantidade"] == 2
        assert loja_a["valor"] == 400.00

    def test_resumo_no_notas(self, client, auth_header, db_session):
        headers, _ = auth_header()

        r = client.get("/v1/dashboard/resumo", headers=headers)
        assert r.status_code == 200
        data = r.json()

        assert data["total_notas"] == 0
        assert data["valor_total"] == 0.0
        assert data["media_por_nota"] is None
        assert data["ultima_extracao"] is None
        assert data["por_mes"] == []
        assert data["por_empresa"] == []

    def test_resumo_isolates_users(self, client, auth_header, db_session):
        headers1, uid1 = auth_header(email="user1@test.com")
        _, uid2 = auth_header(email="user2@test.com")
        self._seed_user_notas(db_session, uid1)

        r = client.get("/v1/dashboard/resumo", headers=headers1)
        assert r.status_code == 200
        assert r.json()["total_notas"] == 3


class TestSoftDeleteMixedActiveInactive:

    def test_listar_notas_mixed_active_inactive_same_chave(self, client, auth_header, db_session):
        headers, uid = auth_header()
        now = datetime.now(timezone.utc)
        chave = "31200611222233300014455555555555555555555555"

        _create_extracao_com_nota(db_session, id_extracao=1, id_usuario=uid)
        _create_extracao_com_nota(db_session, id_extracao=2, id_usuario=uid)

        nota_active = NotaAnalytics(
            id_nota_analytics=1, id_extracao=1, id_usuario=uid,
            chave_acesso=chave,
            empresa="Active Empresa", numero="123456", serie="1",
            emissao=now.date(), valor_total=100.00, qtd_total_itens=1,
            valid_from=now,
            id_importacao=1, id_nota_raw=1, processado_em=now,
            is_active=True,
        )
        db_session.add(nota_active)

        nota_inactive = NotaAnalytics(
            id_nota_analytics=2, id_extracao=2, id_usuario=uid,
            chave_acesso=chave,
            empresa="Inactive Empresa", numero="654321", serie="2",
            emissao=now.date(), valor_total=200.00, qtd_total_itens=2,
            valid_from=now,
            id_importacao=2, id_nota_raw=2, processado_em=now,
            is_active=False,
        )
        db_session.add(nota_inactive)
        db_session.commit()

        r = client.get("/v1/dashboard/notas", headers=headers)
        assert r.status_code == 200
        data = r.json()
        assert len(data) == 1
        assert data[0]["empresa"] == "Active Empresa"
