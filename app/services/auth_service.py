import hashlib
import logging
import secrets
from abc import ABC, abstractmethod
from datetime import datetime, timedelta, timezone
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


_email_sender: Optional[EmailSender] = None


def get_email_sender() -> EmailSender:
    global _email_sender
    if _email_sender is None:
        _email_sender = LogEmailSender()
    return _email_sender


def generate_code() -> str:
    return f"{secrets.randbelow(1_000_000):06d}"


def hash_code(code: str) -> str:
    return hashlib.sha256(code.encode()).hexdigest()


def create_access_token(sub: str) -> str:
    payload = {
        "sub": sub,
        "exp": datetime.now(timezone.utc) + timedelta(hours=1),
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
