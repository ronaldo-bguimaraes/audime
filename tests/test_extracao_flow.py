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
