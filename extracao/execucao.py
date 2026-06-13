from dotenv import load_dotenv
load_dotenv()

from database import SessionLocal
from database.models.extracao import Extracao
from extracao.enum.status import ExtracaoStatus
from user import get_current_user_id


id_usuario = get_current_user_id()


def get_extracao_id():
    with SessionLocal() as db:
        extracao = Extracao(id_usuario=id_usuario)
        db.add(extracao)
        db.commit()
        db.refresh(extracao)
        return extracao.id_extracao


id_extracao = get_extracao_id()


def get_status(id_extracao: int) -> ExtracaoStatus:
    with SessionLocal() as db:
        extracao = db.get(Extracao, id_extracao)
        return extracao.status


def update_status(id_extracao: int, status: ExtracaoStatus) -> ExtracaoStatus:
    with SessionLocal() as db:
        extracao = db.get(Extracao, id_extracao)
        extracao.status = status
        db.commit()
        db.refresh(extracao)
        return extracao.status


print(f"ID da extração: {id_extracao}")

print("Status atual:", get_status(id_extracao))
# print(update_status(id_extracao, ExtracaoStatus.RUNNING))
# print(update_status(id_extracao, ExtracaoStatus.DONE))
