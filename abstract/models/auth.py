import sqlalchemy as sa

from abstract.base import Base


class AuthCode(Base):
    __tablename__ = "auth_code"
    __table_args__ = {"schema": "core"}

    id_auth_code = sa.Column(
        sa.BigInteger().with_variant(sa.Integer(), "sqlite"),
        primary_key=True,
    )
    email = sa.Column(sa.String, nullable=False, index=True)
    code_hash = sa.Column(sa.String(64), nullable=False)
    expires_at = sa.Column(sa.DateTime(timezone=True), nullable=False)
    used = sa.Column(sa.Boolean, default=False)
    attempts = sa.Column(sa.Integer, default=0)
    last_attempt_at = sa.Column(sa.DateTime(timezone=True), nullable=True)
