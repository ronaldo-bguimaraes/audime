from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from abstract.models.core import Usuario
from app.core.deps import get_current_user_id, get_db
from app.services.auth_service import send_code, verify_code

router = APIRouter(prefix="/v1/auth", tags=["auth"])


class CodeRequest(BaseModel):
    email: EmailStr


class CodeResponse(BaseModel):
    status: str
    remaining: int | None = None


class VerifyRequest(BaseModel):
    email: EmailStr
    code: str


class VerifyResponse(BaseModel):
    status: str
    access_token: str | None = None
    id_usuario: int | None = None


class MeResponse(BaseModel):
    id_usuario: int
    nome: str
    email: str


@router.post("/code", response_model=CodeResponse)
def request_code(body: CodeRequest, db: Session = Depends(get_db)):
    result = send_code(body.email, db)
    if result["status"] == "cooldown":
        raise HTTPException(status_code=429, detail=f"Aguarde {result['remaining']}s")
    return CodeResponse(status="sent")


@router.post("/verify", response_model=VerifyResponse)
def verify(body: VerifyRequest, db: Session = Depends(get_db)):
    result = verify_code(body.email, body.code, db)
    if result["status"] != "ok":
        raise HTTPException(status_code=401, detail=result["message"])
    return VerifyResponse(status="ok", access_token=result["access_token"], id_usuario=result["id_usuario"])


@router.get("/me", response_model=MeResponse)
def me(id_usuario: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    user = db.get(Usuario, id_usuario)
    if not user:
        raise HTTPException(status_code=404)
    return MeResponse(id_usuario=user.id_usuario, nome=user.nome, email=user.email)
