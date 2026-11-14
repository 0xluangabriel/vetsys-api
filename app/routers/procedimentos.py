from fastapi import APIRouter, HTTPException, Query
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from app.database import SessionDep
from app.models import Animal, Procedimento, ProcedimentoCreate, ProcedimentoEdit
from app.security import FuncionarioAtual

router = APIRouter(prefix="/procedimentos", tags=["Procedimentos"])

@router.get("/")
def listar_procedimentos(session: SessionDep, usuario: FuncionarioAtual, skip: int = Query(default=0, ge=0), limit: int = Query(default=10, ge=1, le=100)):
    return session.exec(select(Procedimento).order_by(Procedimento.id).offset(skip).limit(limit)).all()

@router.post("/", status_code=201)
def criar_procedimento(dados: ProcedimentoCreate, session: SessionDep, usuario: FuncionarioAtual):
    if session.get(Animal, dados.id_animal) is None:
        raise HTTPException(status_code=404, detail="Animal não encontrado.")
    
    procedimento = Procedimento(**dados.model_dump())
    session.add(procedimento)
    session.commit()
    session.refresh(procedimento)
    return procedimento

@router.put("/{id_procedimento}")
def atualizar_procedimento(id_procedimento: int, dados: ProcedimentoCreate, session: SessionDep, usuario: FuncionarioAtual):
    procedimento = session.get(Procedimento, id_procedimento)
    if procedimento is None:
        raise HTTPException(status_code=404, detail="Procedimento não encontrado")
    if session.get(Animal, dados.id_animal) is None:
        raise HTTPException(status_code=404, detail="Animal não encontrado")
    
    for key, value in dados.model_dump().items():
        setattr(procedimento, key, value)
    
    session.commit()
    session.refresh(procedimento)
    return procedimento

@router.patch("/{id_procedimento}")
def att_parte_procedimento(id_procedimento: int, dados: ProcedimentoEdit, session: SessionDep, usuario: FuncionarioAtual):
    procedimento = session.get(Procedimento, id_procedimento)
    if procedimento is None:
        raise HTTPException(status_code=404, detail="Procedimento não encontrado")
    if dados.id_animal is not None:
        if session.get(Animal, dados.id_animal) is None:
            raise HTTPException(status_code=404, detail="Esse ID de animal está inválido ou não existe.")
    for key, value in dados.model_dump(exclude_unset=True).items():
        setattr(procedimento, key, value)
        
    session.commit()
    session.refresh(procedimento)
    return procedimento

@router.get("/{id_procedimento}")
def buscar_procedimento(id_procedimento: int, session: SessionDep, usuario: FuncionarioAtual):
    procedimento = session.get(Procedimento, id_procedimento)
    if procedimento is None:
        raise HTTPException(status_code=404, detail="Procedimento não encontrado")
    return procedimento

@router.delete("/{id_procedimento}")
def apagar_procedimento(id_procedimento: int, session: SessionDep, usuario: FuncionarioAtual):
    procedimento = session.get(Procedimento, id_procedimento)
    if procedimento is None:
        raise HTTPException(status_code=404, detail="Procedimento não encontrado.")
    session.delete(procedimento)
    session.commit()
    return {"mensagem": "Procedimento apagado com sucesso."}
