import hashlib
import logging
import secrets
import smtplib
from abc import ABC, abstractmethod
from datetime import datetime, timedelta, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

import jwt
from sqlalchemy.orm import Session

from abstract.models.auth import AuthCode
from abstract.models.core import Usuario
from app.core.config import settings

logger = logging.getLogger("audime.auth")


class EmailSender(ABC):
    @abstractmethod
    def send_code(self, email: str, code: str) -> None: ...


class LogEmailSender(EmailSender):
    def send_code(self, email: str, code: str) -> None:
        logger.info(f"[DEV] Código para {email}: {code}")
        print(f"[DEV] Código de verificação para {email}: {code}")


class SmtpEmailSender(EmailSender):
    def send_code(self, email: str, code: str) -> None:
        html = f"""\
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="font-family:sans-serif;color:#333;max-width:480px;margin:0 auto">
<div style="text-align:center;padding:32px 0">
<img src="https://www.gstatic.com/mobilesdk/200426_mobilesdk/auth_service_illustration/1x/illustration_2x.png" alt="" width="72" height="72" style="border-radius:12px">
<h1 style="font-size:20px;margin:16px 0 8px">Código de verificação</h1>
<p style="color:#666;font-size:14px;margin:0">Use o código abaixo para acessar sua conta</p>
</div>
<div style="background:#f5f5f5;border-radius:12px;padding:24px;text-align:center">
<span style="font-size:36px;letter-spacing:8px;font-weight:700;color:#1a1a1a">{code}</span>
<p style="color:#999;font-size:12px;margin:16px 0 0">Válido por 5 minutos</p>
</div>
<p style="color:#999;font-size:12px;text-align:center;margin-top:24px">Se você não solicitou este código, ignore este email.</p>
<p style="color:#bbb;font-size:11px;text-align:center">Audime — Gestão Financeira</p>
</body>
</html>"""

        text = f"Seu código de verificação: {code}\n\nVálido por 5 minutos.\n\nSe você não solicitou este código, ignore este email."

        msg = MIMEMultipart("alternative")
        msg.attach(MIMEText(text, "plain"))
        msg.attach(MIMEText(html, "html"))

        msg["Subject"] = f"Seu código de verificação Audime: {code}"
        msg["From"] = f"{settings.mail_from_name} <{settings.mail_from}>"
        msg["To"] = email
        msg["X-Mailer"] = "Audime"

        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as server:
            server.starttls()
            server.login(settings.smtp_user, settings.smtp_password)
            server.send_message(msg)

        logger.info(f"Verification code sent to {email}")


_email_sender: Optional[EmailSender] = None


def get_email_sender() -> EmailSender:
    global _email_sender
    if _email_sender is None:
        if settings.smtp_password and settings.app_env == "production":
            _email_sender = SmtpEmailSender()
        else:
            _email_sender = LogEmailSender()
    return _email_sender


def override_email_sender(sender: EmailSender) -> None:
    global _email_sender
    _email_sender = sender


def generate_code() -> str:
    return f"{secrets.randbelow(1_000_000):06d}"


def hash_code(code: str) -> str:
    return hashlib.sha256(code.encode()).hexdigest()


def create_access_token(sub: str) -> str:
    payload = {
        "sub": sub,
        "exp": datetime.now(timezone.utc) + timedelta(days=7),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except jwt.PyJWTError:
        return None


COOLDOWN_SECONDS = 60
MAX_ATTEMPTS = 5


def send_code(email: str, db: Session) -> dict:
    email = email.strip().lower()

    existing = (
        db.query(AuthCode)
        .filter(AuthCode.email == email, AuthCode.used == False)
        .order_by(AuthCode.expires_at.desc())
        .first()
    )
    if existing:
        expires_at = existing.expires_at.replace(tzinfo=timezone.utc) if existing.expires_at.tzinfo is None else existing.expires_at
        if expires_at > datetime.now(timezone.utc):
            last_attempt = existing.last_attempt_at.replace(tzinfo=timezone.utc) if existing.last_attempt_at and existing.last_attempt_at.tzinfo is None else existing.last_attempt_at
            elapsed = (datetime.now(timezone.utc) - (last_attempt or expires_at - timedelta(minutes=5))).total_seconds()
            if elapsed < COOLDOWN_SECONDS:
                remaining = int(COOLDOWN_SECONDS - elapsed)
                return {"status": "cooldown", "remaining": remaining}

    code = generate_code()
    code_hash = hash_code(code)

    auth_code = AuthCode(
        email=email,
        code_hash=code_hash,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=5),
    )
    db.add(auth_code)
    db.commit()

    sender = get_email_sender()
    sender.send_code(email, code)

    return {"status": "sent"}


def verify_code(email: str, code: str, db: Session) -> dict:
    email = email.strip().lower()

    pending = (
        db.query(AuthCode)
        .filter(AuthCode.email == email, AuthCode.used == False)
        .order_by(AuthCode.expires_at.desc())
        .first()
    )

    if not pending:
        return {"status": "error", "message": "Código expirado ou não encontrado"}

    expires_at = pending.expires_at.replace(tzinfo=timezone.utc) if pending.expires_at.tzinfo is None else pending.expires_at
    if expires_at < datetime.now(timezone.utc):
        return {"status": "error", "message": "Código expirado ou não encontrado"}

    pending.attempts += 1
    pending.last_attempt_at = datetime.now(timezone.utc)
    db.commit()

    if pending.attempts > MAX_ATTEMPTS:
        return {"status": "error", "message": "Muitas tentativas. Solicite um novo código."}

    if pending.code_hash != hash_code(code):
        return {"status": "error", "message": "Código inválido"}

    pending.used = True
    db.commit()

    user = db.query(Usuario).filter(Usuario.email == email).first()
    if not user:
        name = email.split("@")[0]
        user = Usuario(nome=name, email=email)
        db.add(user)
        db.commit()
        db.refresh(user)

    token = create_access_token(str(user.id_usuario))

    return {"status": "ok", "access_token": token, "id_usuario": user.id_usuario}
