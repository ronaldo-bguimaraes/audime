import re


def test_auth_flow(client, auth_header):
    prints = []

    import app.services.auth_service as auth_mod
    auth_mod.override_email_sender(auth_mod.LogEmailSender())
    original = auth_mod.LogEmailSender.send_code

    def fake(self, email, code):
        prints.append((email, code))

    auth_mod.LogEmailSender.send_code = fake

    r = client.post("/v1/auth/code", json={"email": "user@test.com"})
    assert r.status_code == 200
    assert r.json()["status"] == "sent"

    assert len(prints) == 1
    email, code = prints[0]
    assert email == "user@test.com"
    assert re.match(r"^\d{6}$", code)

    r = client.post("/v1/auth/verify", json={"email": "user@test.com", "code": code})
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert data["access_token"] is not None
    assert data["id_usuario"] == 1

    token = data["access_token"]

    r = client.get("/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    me = r.json()
    assert me["email"] == "user@test.com"
    assert me["nome"] == "user"

    auth_mod.LogEmailSender.send_code = original


def test_auth_invalid_code(client, auth_header):
    import app.services.auth_service as auth_mod
    auth_mod.override_email_sender(auth_mod.LogEmailSender())
    original = auth_mod.LogEmailSender.send_code
    auth_mod.LogEmailSender.send_code = lambda self, e, c: None

    client.post("/v1/auth/code", json={"email": "user@test.com"})
    r = client.post("/v1/auth/verify", json={"email": "user@test.com", "code": "000000"})
    assert r.status_code == 401

    auth_mod.LogEmailSender.send_code = original


def test_auth_no_token(client):
    r = client.get("/v1/auth/me")
    assert r.status_code in (401, 403)
