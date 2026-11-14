from fastapi import APIRouter, HTTPException, Query
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from app.database import SessionDep
from app.models import Animal, Procedimento
from app.security import TutorAtual

router = APIRouter(prefix="/meus", tags=["Meus"])

@router.get("/animais")
def listar_proprios_animais(session: SessionDep, usuario: TutorAtual, skip: int = Query(default=0, ge=0), limit: int = Query(default=10, ge=1, le=100)):
    return session.exec(select(Animal).order_by(Animal.id).where(Animal.id_tutor == usuario.id_tutor).offset(skip).limit(limit)).all()

@router.get("/procedimentos")
def listar_proprios_procedimentos(session: SessionDep, usuario: TutorAtual, skip: int = Query(default=0, ge=0), limit: int = Query(default=10, ge=1, le=100)):
    return session.exec(select(Procedimento).join(Animal, Procedimento.id_animal == Animal.id).order_by(Procedimento.data.desc()).where(Animal.id_tutor == usuario.id_tutor).offset(skip).limit(limit)).all()
