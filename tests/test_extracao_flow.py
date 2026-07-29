from datetime import datetime, timezone

from abstract.models.core import Extracao, ExtracaoStatus, Usuario


def _ensure_usuario(db_session, id_usuario):
    u = db_session.get(Usuario, id_usuario)
    if u is None:
        u = Usuario(id_usuario=id_usuario, nome="Test User", email=f"user{id_usuario}@test.com")
        db_session.add(u)
        db_session.flush()


def test_list_extracao_empty(client, auth_header):
    headers, _ = auth_header()
    r = client.get("/v1/extracoes", headers=headers)
    assert r.status_code == 200
    assert r.json() == []


def test_list_extracao_returns_user_extracoes(client, auth_header, db_session):
    headers1, uid1 = auth_header(email="user1@test.com")
    headers2, uid2 = auth_header(email="user2@test.com")

    _ensure_usuario(db_session, uid1)
    _ensure_usuario(db_session, uid2)

    now = datetime.now(timezone.utc)
    e1 = Extracao(
        id_extracao=1,
        id_usuario=uid1,
        status=ExtracaoStatus.DONE,
        created_at=now,
    )
    e2 = Extracao(
        id_extracao=2,
        id_usuario=uid1,
        status=ExtracaoStatus.PENDING,
        created_at=now,
    )
    e3 = Extracao(
        id_extracao=3,
        id_usuario=uid2,
        status=ExtracaoStatus.DONE,
        created_at=now,
    )
    db_session.add_all([e1, e2, e3])
    db_session.commit()

    r1 = client.get("/v1/extracoes", headers=headers1)
    assert r1.status_code == 200
    data = r1.json()
    assert len(data) == 2
    ids1 = {d["id_extracao"] for d in data}
    assert ids1 == {1, 2}

    for d in data:
        assert "url" in d

    r2 = client.get("/v1/extracoes", headers=headers2)
    assert r2.status_code == 200
    r2_data = r2.json()
    assert len(r2_data) == 1
    assert r2_data[0]["id_extracao"] == 3
    for d in r2_data:
        assert "url" in d


def test_list_extracao_limit(client, auth_header, db_session):
    headers, uid = auth_header()

    _ensure_usuario(db_session, uid)

    now = datetime.now(timezone.utc)
    for i in range(5):
        e = Extracao(
            id_extracao=i + 1,
            id_usuario=uid,
            status=ExtracaoStatus.PENDING,
            created_at=now,
        )
        db_session.add(e)
    db_session.commit()

    r = client.get("/v1/extracoes?limit=3", headers=headers)
    assert r.status_code == 200
    assert len(r.json()) == 3


def test_list_extracao_unauthorized(client):
    r = client.get("/v1/extracoes")
    assert r.status_code in (401, 403)


# ── Force-reset endpoint (Issue #12: Stuck PENDING recovery) ────────


def test_force_reset_pending_to_error(client, auth_header, db_session):
    """Force-reset transitions PENDING -> ERROR with a message."""
    headers, uid = auth_header()
    _ensure_usuario(db_session, uid)
    now = datetime.now(timezone.utc)
    e = Extracao(
        id_extracao=100,
        id_usuario=uid,
        status=ExtracaoStatus.PENDING,
        created_at=now,
    )
    db_session.add(e)
    db_session.commit()

    r = client.post(
        "/v1/extracoes/100/force-reset",
        json={"mensagem": "Worker timeout - stuck pending"},
        headers=headers,
    )
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ERROR"
    assert "mensagem" in data


def test_force_reset_not_found(client, auth_header):
    """Force-reset returns 404 for non-existent extraction."""
    headers, _ = auth_header()
    r = client.post(
        "/v1/extracoes/99999/force-reset",
        json={"mensagem": "test"},
        headers=headers,
    )
    assert r.status_code == 404


def test_force_reset_wrong_user(client, auth_header, db_session):
    """Force-reset returns 404 for another user's extraction."""
    headers1, uid1 = auth_header(email="user1@test.com")
    headers2, uid2 = auth_header(email="user2@test.com")
    _ensure_usuario(db_session, uid1)
    _ensure_usuario(db_session, uid2)
    now = datetime.now(timezone.utc)
    e = Extracao(
        id_extracao=101,
        id_usuario=uid1,
        status=ExtracaoStatus.PENDING,
        created_at=now,
    )
    db_session.add(e)
    db_session.commit()

    r = client.post(
        "/v1/extracoes/101/force-reset",
        json={"mensagem": "test"},
        headers=headers2,
    )
    assert r.status_code == 404


def test_force_reset_done_not_allowed(client, auth_header, db_session):
    """Force-reset returns 409 for DONE extraction (not stuck)."""
    headers, uid = auth_header()
    _ensure_usuario(db_session, uid)
    now = datetime.now(timezone.utc)
    e = Extracao(
        id_extracao=102,
        id_usuario=uid,
        status=ExtracaoStatus.DONE,
        created_at=now,
    )
    db_session.add(e)
    db_session.commit()

    r = client.post(
        "/v1/extracoes/102/force-reset",
        json={"mensagem": "test"},
        headers=headers,
    )
    assert r.status_code == 409


def test_force_reset_running_not_allowed(client, auth_header, db_session):
    """Force-reset returns 409 for RUNNING extraction (still active)."""
    headers, uid = auth_header()
    _ensure_usuario(db_session, uid)
    now = datetime.now(timezone.utc)
    e = Extracao(
        id_extracao=103,
        id_usuario=uid,
        status=ExtracaoStatus.RUNNING,
        created_at=now,
    )
    db_session.add(e)
    db_session.commit()

    r = client.post(
        "/v1/extracoes/103/force-reset",
        json={"mensagem": "test"},
        headers=headers,
    )
    assert r.status_code == 409


def test_force_reset_error_not_allowed(client, auth_header, db_session):
    """Force-reset returns 409 for ERROR extraction (already terminated)."""
    headers, uid = auth_header()
    _ensure_usuario(db_session, uid)
    now = datetime.now(timezone.utc)
    e = Extracao(
        id_extracao=104,
        id_usuario=uid,
        status=ExtracaoStatus.ERROR,
        created_at=now,
    )
    db_session.add(e)
    db_session.commit()

    r = client.post(
        "/v1/extracoes/104/force-reset",
        json={"mensagem": "test"},
        headers=headers,
    )
    assert r.status_code == 409


def test_force_reset_preserves_imports(client, auth_header, db_session):
    """Force-reset preserves existing import data (does not delete history)."""
    from abstract.models.raw import Importacao

    headers, uid = auth_header()
    _ensure_usuario(db_session, uid)
    now = datetime.now(timezone.utc)
    e = Extracao(
        id_extracao=105,
        id_usuario=uid,
        status=ExtracaoStatus.PENDING,
        created_at=now,
    )
    db_session.add(e)
    db_session.commit()

    imp = Importacao(
        id_importacao=105,
        storage_bucket="test",
        storage_key="test/105",
        storage_filename="file105.html",
        sha256="0" * 64,
        imported_at=now,
        id_extracao=105,
        id_usuario=uid,
    )
    db_session.add(imp)
    db_session.commit()

    r = client.post(
        "/v1/extracoes/105/force-reset",
        json={"mensagem": "test"},
        headers=headers,
    )
    assert r.status_code == 200

    # Import should still exist
    imp_count = db_session.query(Importacao).filter(
        Importacao.id_extracao == 105
    ).count()
    assert imp_count == 1
