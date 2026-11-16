from fastapi import APIRouter, HTTPException, Query
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from app.database import SessionDep
from app.models import Tutor, TutorCreate, TutorEdit
from app.security import FuncionarioAtual

router = APIRouter(prefix="/tutores", tags=["Tutores"])

@router.post("", status_code=201)
def criar_tutor(dados: TutorCreate, session: SessionDep, usuario: FuncionarioAtual):
    tutor = Tutor(**dados.model_dump())
    if dados.email and session.exec(select(Tutor).where(Tutor.email == dados.email)).first():
        raise HTTPException(status_code=409, detail="Email já cadastrado")
    session.add(tutor)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409, detail="E-mail já cadastrado")
    session.refresh(tutor)
    return tutor

@router.put("/{id_tutor}")
def atualizar_tutor(id_tutor: int, dados: TutorCreate, session: SessionDep, usuario: FuncionarioAtual):
    tutor = session.get(Tutor, id_tutor)
    if tutor is None:
        raise HTTPException(status_code=404, detail="Tutor não encontrado")
    
    for key, value in dados.model_dump().items():
        setattr(tutor, key, value)
    
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409, detail="E-mail já cadastrado")
    session.refresh(tutor)
    return tutor

@router.get("")
def listar_tutores(session: SessionDep, usuario: FuncionarioAtual, skip: int = Query(default=0, ge=0), limit: int = Query(default=10, ge=1, le=100)):
    return session.exec(select(Tutor).order_by(Tutor.id).offset(skip).limit(limit)).all()

@router.get("/{id_tutor}")
def buscar_tutor(id_tutor: int, session: SessionDep, usuario: FuncionarioAtual):
    tutor = session.get(Tutor, id_tutor)
    if tutor is None:
        raise HTTPException(status_code=404, detail="Tutor não encontrado")
    return tutor

@router.delete("/{id_tutor}")
def apagar_tutor(id_tutor: int, session: SessionDep, usuario: FuncionarioAtual):
    tutor = session.get(Tutor, id_tutor)
    if tutor is None:
        raise HTTPException(status_code=404, detail="Tutor não encontrado")
    session.delete(tutor)
    session.commit()
    return {"mensagem": "Tutor, seus animais e procedimentos foram excluídos com sucesso."}

@router.get("/{id_tutor}/animais")
def buscar_animais_tutor(id_tutor: int, session: SessionDep, usuario: FuncionarioAtual):
    tutor = session.get(Tutor, id_tutor)
    if tutor is None:
        raise HTTPException(status_code=404, detail="Tutor inválido ou não encontrado")
    return tutor.animais

@router.patch("/{id_tutor}")
def att_parte_tutor(id_tutor: int, dados: TutorEdit, session: SessionDep, usuario: FuncionarioAtual):
    tutor = session.get(Tutor, id_tutor)
    if tutor is None:
        raise HTTPException(status_code=404, detail="Tutor não encontrado")
    for key, value in dados.model_dump(exclude_unset=True).items():
        setattr(tutor, key, value)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409, detail="E-mail já cadastrado")
    session.refresh(tutor)
    return tutor