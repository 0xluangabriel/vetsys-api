from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, field_validator
from sqlmodel import SQLModel, Field, create_engine, Session, select, Relationship
from sqlalchemy.exc import IntegrityError
from typing import Annotated
from enum import Enum
from datetime import date
import os
from dotenv import load_dotenv

class TutorCreate(SQLModel):
    nome: str = Field(min_length=1, max_length=100)
    email: str = Field(max_length=150, unique=True)
    telefone: str = Field(regex=r"^\d+$", max_length=11)

class Tutor(TutorCreate, table=True):
    id: int | None = Field(default=None, primary_key=True)
    animais: list["Animal"] = Relationship(back_populates="tutor", cascade_delete=True)

class TutorEdit(SQLModel):
    nome: str | None = Field(default=None, min_length=1, max_length=100)
    email: str | None = Field(default=None, max_length=150, unique=True)
    telefone: str | None = Field(default=None, regex=r"^\d+$", max_length=11)


class AnimalCreate(SQLModel):
    id_tutor: int = Field(foreign_key="tutor.id", ondelete="CASCADE")
    nome: str = Field(min_length=1, max_length=100)
    especie: str = Field(min_length=1, max_length=50)
    raca: str = Field(min_length=1, max_length=50)
    sexo: str = Field(min_length=1, max_length=1)
    idade: str = Field(max_length=20)
    peso: float = Field(gt=0, lt=500)

class Animal(AnimalCreate, table=True):
    id: int | None = Field(default=None, primary_key=True)
    tutor: Tutor | None = Relationship(back_populates="animais")
    procedimentos: list["Procedimento"] = Relationship(back_populates="animal", cascade_delete=True)

class AnimalEdit(SQLModel):
    id_tutor: int | None = None
    nome: str | None = Field(default=None, min_length=1, max_length=100)
    especie: str | None = Field(default=None, min_length=1, max_length=50)
    raca: str | None = Field(default=None, min_length=1, max_length=50)
    sexo: str | None = Field(default=None, min_length=1, max_length=1)
    idade: str | None = Field(default=None, max_length=20)
    peso: float | None = Field(default=None, gt=0, lt=500)

class TipoProcedimento(str, Enum):
    vacinacao = "Vacinação"
    castracao = "Castração"
    exame = "Exame"
    consulta = "Consulta"
    cirurgia = "Cirurgia"

class ProcedimentoCreate(SQLModel):
    id_animal: int = Field(foreign_key="animal.id", ondelete="CASCADE")
    nome: str = Field(min_length=1, max_length=100)
    descricao: str = Field(min_length=1, max_length=500)
    preco: float
    tipo: TipoProcedimento
    data: date

    @field_validator("data")
    @classmethod
    def data_nao_pode_ser_passada(cls, valor):
        if valor < date.today():
            raise ValueError("A data não pode ser anterior ao dia de hoje.")
        return valor

class ProcedimentoEdit(SQLModel):
    nome: str | None = Field(default=None, min_length=1, max_length=100)
    descricao: str | None = Field(default=None, min_length=1, max_length=500)
    preco: float | None = None
    tipo: TipoProcedimento | None = None
    data: date | None = None
    id_animal: int | None = None

class Procedimento(ProcedimentoCreate, table=True):
    id: int | None = Field(default=None, primary_key=True)
    animal: Animal | None = Relationship(back_populates="procedimentos")


load_dotenv()
engine = create_engine(os.getenv("DATABASE_URL"))
SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

app = FastAPI(title="Vetsys API", description="API para gerenciamento de tutores e pets", version="1.7.0")
SessionDep = Annotated[Session, Depends(get_session)]



#----------PROCEDIMENTOS----------
@app.get("/procedimentos")
def listar_procedimentos(session: SessionDep, skip: int = 0, limit: int = 10):
    return session.exec(select(Procedimento).offset(skip).limit(limit)).all()

@app.post("/procedimentos", status_code=201)
def criar_procedimento(dados: ProcedimentoCreate, session: SessionDep):
    if session.get(Animal, dados.id_animal) is None:
        raise HTTPException(status_code=404, detail="Animal não encontrado")
    
    procedimento = Procedimento(**dados.model_dump())
    session.add(procedimento)
    session.commit()
    session.refresh(procedimento)
    return procedimento

@app.put("/procedimentos/{id_procedimento}")
def atualizar_procedimento(id_procedimento: int, dados: ProcedimentoCreate, session: SessionDep):
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

@app.patch("/procedimentos/{id_procedimento}")
def att_parte_procedimento(id_procedimento: int, dados: ProcedimentoEdit, session: SessionDep):
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

@app.get("/procedimentos/{id_procedimento}")
def buscar_procedimento(id_procedimento: int, session: SessionDep):
    procedimento = session.get(Procedimento, id_procedimento)
    if procedimento is None:
        raise HTTPException(status_code=404, detail="Procedimento não encontrado")
    return procedimento

@app.delete("/procedimentos/{id_procedimento}")
def apagar_procedimento(id_procedimento: int, session: SessionDep):
    procedimento = session.get(Procedimento, id_procedimento)
    if procedimento is None:
        raise HTTPException(status_code=404, detail="Procedimento não encontrado.")
    session.delete(procedimento)
    session.commit()
    return {"mensagem": "Procedimento apagado com sucesso."}

#----------ANIMAIS----------
@app.get("/animais")
def listar_animais(session: SessionDep, skip: int = 0, limit: int = 10):
    return session.exec(select(Animal).offset(skip).limit(limit)).all()

@app.post("/animais", status_code=201)
def criar_animal(dados: AnimalCreate, session: SessionDep):
    if session.get(Tutor, dados.id_tutor) is None:
        raise HTTPException(status_code=404, detail="ID de Tutor inválido ou não encontrado.")
    animal = Animal(**dados.model_dump())
    session.add(animal)
    session.commit()
    session.refresh(animal)
    return animal

@app.put("/animais/{id_animal}")
def atualizar_animal(id_animal: int, dados: AnimalCreate, session: SessionDep):
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

@app.get("/animais/{id_animal}")
def buscar_animal(id_animal: int, session: SessionDep):
    animal = session.get(Animal, id_animal)
    if animal is None:
        raise HTTPException(status_code=404, detail="Animal não encontrado")
    return animal

@app.delete("/animais/{id_animal}")
def apagar_animal(id_animal: int, session: SessionDep):
    animal = session.get(Animal, id_animal)
    if animal is None:
        raise HTTPException(status_code=404, detail="Animal não encontrado.")
    procedimentos = session.exec(select(Procedimento).where(Procedimento.id_animal == animal.id)).all()
    for procedimento in procedimentos:
        session.delete(procedimento)
    session.delete(animal)
    session.commit()
    return {"mensagem": "Animal apagado com sucesso."}

@app.get("/animais/{id_animal}/procedimentos")
def buscar_procedimentos_animal(id_animal: int, session: SessionDep):
    animal = session.get(Animal, id_animal)
    if animal is None:
        raise HTTPException(status_code=404, detail="ID de animal inválido ou não encontrado")
    procedimentos = session.exec(select(Procedimento).where(Procedimento.id_animal == animal.id).order_by(Procedimento.data)).all()
    return procedimentos

@app.get("/animais/{id_animal}/vacinas")
def buscar_vacinas_animal(id_animal: int, session: SessionDep):
    animal = session.get(Animal, id_animal)
    if animal is None:
        raise HTTPException(status_code=404, detail="ID de animal inválido ou não encontrado")
    vacinas = session.exec(select(Procedimento).where(Procedimento.id_animal == animal.id, Procedimento.tipo == TipoProcedimento.vacinacao).order_by(Procedimento.data)).all()
    return vacinas

@app.patch("/animais/{id_animal}")
def att_parte_animal(id_animal: int, dados: AnimalEdit, session: SessionDep):
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

#----------TUTORES----------
@app.post("/tutores", status_code=201)
def criar_tutor(dados: TutorCreate, session: SessionDep):
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

@app.put("/tutores/{id_tutor}")
def atualizar_tutor(id_tutor: int, dados: TutorCreate, session: SessionDep):
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

@app.get("/tutores")
def listar_tutores(session: SessionDep, skip: int = 0, limit: int = 10):
    return session.exec(select(Tutor).offset(skip).limit(limit)).all()

@app.get("/tutores/{id_tutor}")
def buscar_tutor(id_tutor: int, session: SessionDep):
    tutor = session.get(Tutor, id_tutor)
    if tutor is None:
        raise HTTPException(status_code=404, detail="Tutor não encontrado")
    return tutor

@app.delete("/tutores/{id_tutor}")
def apagar_tutor(id_tutor: int, session: SessionDep):
    tutor = session.get(Tutor, id_tutor)
    if tutor is None:
        raise HTTPException(status_code=404, detail="Tutor não encontrado")
    animais = session.exec(select(Animal).where(Animal.id_tutor == tutor.id)).all()
    for animal in animais:
        procedimentos = session.exec(select(Procedimento).where(Procedimento.id_animal == animal.id)).all()
        for procedimento in procedimentos:
            session.delete(procedimento)
        session.delete(animal)
    session.delete(tutor)
    session.commit()
    return {"mensagem": "Tutor, seus animais e procedimentos foram excluídos com sucesso."}

@app.get("/tutores/{id_tutor}/animais")
def buscar_animais_tutor(id_tutor: int, session: SessionDep):
    tutor = session.get(Tutor, id_tutor)
    if tutor is None:
        raise HTTPException(status_code=404, detail="Tutor inválido ou não encontrado")
    animais = session.exec(select(Animal).where(Animal.id_tutor == tutor.id)).all()
    return animais

@app.patch("/tutores/{id_tutor}")
def att_parte_tutor(id_tutor: int, dados: TutorEdit, session: SessionDep):
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