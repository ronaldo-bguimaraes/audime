"""Testes para o campo url na model Extracao."""

from datetime import datetime, timezone

import pytest

from abstract.models.core import Extracao, ExtracaoStatus, Usuario


def _ensure_usuario(db_session, id_usuario):
    u = db_session.get(Usuario, id_usuario)
    if u is None:
        u = Usuario(id_usuario=id_usuario, nome="Test User", email=f"user{id_usuario}@test.com")
        db_session.add(u)
        db_session.flush()


class TestUrlField:
    """Testes para o campo url na model Extracao."""

    def test_create_extracao_saves_url(self, client, auth_header):
        """POST salva url e retorna no GET list."""
        headers, _ = auth_header()
        test_url = "https://www.sefaz.mt.gov.br/nfce/consultanfce?p=41160600000000000000651230000000001234567890"

        r = client.post(
            "/v1/extracoes",
            json={"url": test_url},
            headers=headers,
        )
        assert r.status_code == 202
        post_data = r.json()
        assert "id_extracao" in post_data

        r2 = client.get("/v1/extracoes", headers=headers)
        assert r2.status_code == 200
        extracoes = r2.json()
        assert len(extracoes) >= 1
        newest = extracoes[0]
        assert "url" in newest
        assert newest["url"] == test_url

    def test_get_extracao_by_id_returns_url(self, client, auth_header):
        """GET por id retorna url."""
        headers, _ = auth_header()
        test_url = "https://www.sefaz.mt.gov.br/nfce/consultanfce?p=123"

        r = client.post(
            "/v1/extracoes",
            json={"url": test_url},
            headers=headers,
        )
        post_data = r.json()
        id_extracao = post_data["id_extracao"]

        r2 = client.get(
            f"/v1/extracoes/{id_extracao}",
            headers=headers,
        )
        assert r2.status_code == 200
        data = r2.json()
        assert data["url"] == test_url

    def test_url_nullable_for_old_records(self, client, auth_header, db_session):
        """Extracao criado diretamente sem url deve retornar url: None."""
        headers, uid = auth_header()

        _ensure_usuario(db_session, uid)

        now = datetime.now(timezone.utc)
        e = Extracao(
            id_usuario=uid,
            status=ExtracaoStatus.DONE,
            created_at=now,
        )
        db_session.add(e)
        db_session.commit()

        r = client.get("/v1/extracoes", headers=headers)
        assert r.status_code == 200
        data = r.json()
        for item in data:
            if item["id_extracao"] == e.id_extracao:
                assert "url" in item
                assert item["url"] is None
                break
        else:
            pytest.fail("Record not found")
