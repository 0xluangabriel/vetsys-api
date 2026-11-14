from fastapi import APIRouter, HTTPException, Query
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from app.database import SessionDep
from app.models import Tutor, Procedimento, TipoProcedimento, Animal, AnimalCreate, AnimalEdit
from app.security import FuncionarioAtual

router = APIRouter(prefix="/animais", tags=["Animais"])

@router.get("/")
def listar_animais(session: SessionDep, usuario: FuncionarioAtual, skip: int = Query(default=0, ge=0), limit: int = Query(default=10, ge=1, le=100)):
    return session.exec(select(Animal).order_by(Animal.id).offset(skip).limit(limit)).all()

@router.post("/", status_code=201)
def criar_animal(dados: AnimalCreate, session: SessionDep, usuario: FuncionarioAtual):
    if session.get(Tutor, dados.id_tutor) is None:
        raise HTTPException(status_code=404, detail="ID de Tutor inválido ou não encontrado.")
    animal = Animal(**dados.model_dump())
    session.add(animal)
    session.commit()
    session.refresh(animal)
    return animal

@router.put("/{id_animal}")
def atualizar_animal(id_animal: int, dados: AnimalCreate, session: SessionDep, usuario: FuncionarioAtual):
    animal = session.get(Animal, id_animal)
    if animal is None:
        raise HTTPException(status_code=404, detail="ID de Animal inválido ou não encontrado.")
    if session.get(Tutor, dados.id_tutor) is None:
        raise HTTPException(status_code=404, detail="ID de Tutor inválido ou não encontrado.")
    
    
    for key, value in dados.model_dump().items():
        setattr(animal, key, value)
    
    session.commit()
    session.refresh(animal)
    return animal

@router.get("/{id_animal}")
def buscar_animal(id_animal: int, session: SessionDep, usuario: FuncionarioAtual):
    animal = session.get(Animal, id_animal)
    if animal is None:
        raise HTTPException(status_code=404, detail="Animal não encontrado")
    return animal

@router.delete("/{id_animal}")
def apagar_animal(id_animal: int, session: SessionDep, usuario: FuncionarioAtual):
    animal = session.get(Animal, id_animal)
    if animal is None:
        raise HTTPException(status_code=404, detail="Animal não encontrado.")
    session.delete(animal)
    session.commit()
    return {"mensagem": "Animal apagado com sucesso."}

@router.get("/{id_animal}/procedimentos")
def buscar_procedimentos_animal(id_animal: int, session: SessionDep, usuario: FuncionarioAtual):
    animal = session.get(Animal, id_animal)
    if animal is None:
        raise HTTPException(status_code=404, detail="ID de animal inválido ou não encontrado")
    procedimentos = session.exec(select(Procedimento).where(Procedimento.id_animal == animal.id).order_by(Procedimento.data)).all()
    return procedimentos

@router.get("/{id_animal}/vacinas")
def buscar_vacinas_animal(id_animal: int, session: SessionDep, usuario: FuncionarioAtual):
    animal = session.get(Animal, id_animal)
    if animal is None:
        raise HTTPException(status_code=404, detail="ID de animal inválido ou não encontrado")
    vacinas = session.exec(select(Procedimento).where(Procedimento.id_animal == animal.id, Procedimento.tipo == TipoProcedimento.vacinacao).order_by(Procedimento.data)).all()
    return vacinas

@router.patch("/{id_animal}")
def att_parte_animal(id_animal: int, dados: AnimalEdit, session: SessionDep, usuario: FuncionarioAtual):
    animal = session.get(Animal, id_animal)
    if animal is None:
        raise HTTPException(status_code=404, detail="Animal não encontrado")
    if dados.id_tutor is not None:
        if session.get(Tutor, dados.id_tutor) is None:
            raise HTTPException(status_code=404, detail="Esse ID de tutor está inválido ou não existe.")    
    for key, value in dados.model_dump(exclude_unset=True).items():
        setattr(animal, key, value)
    session.commit()
    session.refresh(animal)
    return animal
