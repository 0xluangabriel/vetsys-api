from sqlmodel import SQLModel, Field, create_engine, Session, select, Relationship
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from datetime import date, datetime, timedelta, timezone
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator, ValidationInfo
from sqlalchemy.exc import IntegrityError
from pwdlib import PasswordHash
from dotenv import load_dotenv
from typing import Annotated
from enum import Enum
import os
import jwt

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITMO = "HS256"
MINUTOS_EXPIRACAO = 30



class UsuarioCreate(SQLModel):
    nome: str = Field(min_length=1, max_length=100)
    email: str = Field(max_length=150)
    senha: str = Field(max_length=128)

    @field_validator("senha")
    @classmethod
    def senha_forte(cls, valor):
        if len(valor) < 8:
            raise ValueError("A senha precisa ter no mínimo 8 caracteres.")
        return valor
    
class UsuarioOut(SQLModel):
    nome: str
    email: str

class PerfilUsuario(str, Enum):
    comum = "comum"
    funcionario = "funcionario"
    admin = "admin"

class PerfilEdit(SQLModel):
    perfil: PerfilUsuario

class Usuario(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nome: str = Field(max_length=100)
    email: str = Field(max_length=150, unique=True)
    senha_hash: str = Field(max_length=255)
    perfil: PerfilUsuario = Field(default=PerfilUsuario.comum)

class UsuarioAdminOut(SQLModel):
    id: int
    nome: str
    email: str
    perfil: PerfilUsuario

class TutorCreate(SQLModel):
    nome: str = Field(min_length=1, max_length=100)
    email: str = Field(max_length=150, unique=True)
    telefone: str = Field(regex=r"^\d+$", max_length=11)
    endereco: str = Field(min_length=1, max_length=200)
    cep: str = Field(regex=r"^\d{8}$", max_length=8)

class Tutor(TutorCreate, table=True):
    id: int | None = Field(default=None, primary_key=True)
    animais: list["Animal"] = Relationship(back_populates="tutor", cascade_delete=True)

class TutorEdit(SQLModel):
    nome: str | None = Field(default=None, min_length=1, max_length=100)
    email: str | None = Field(default=None, max_length=150, unique=True)
    telefone: str | None = Field(default=None, regex=r"^\d+$", max_length=11)
    endereco: str | None = Field(default=None, min_length=1, max_length=200)
    cep: str | None = Field(default=None, regex=r"^\d{8}$")

    @field_validator("endereco", "cep")
    @classmethod
    def nao_pode_ser_nulo(cls, valor, info: ValidationInfo):
        if valor is None:
            raise ValueError("O campo {} não pode estar vazio.".format(info.field_name))
        return valor
    
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

class FormaPagamento(str, Enum):
    credito = "Cartão de Crédito"
    debito = "Cartão de Débito"
    pix = "Pix"
    dinheiro = "Dinheiro"

class ProcedimentoCreate(SQLModel):
    id_animal: int = Field(foreign_key="animal.id", ondelete="CASCADE")
    nome: str = Field(min_length=1, max_length=100)
    descricao: str = Field(min_length=1, max_length=500)
    preco: float
    tipo: TipoProcedimento
    forma_pagamento: FormaPagamento | None = None
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
    forma_pagamento: FormaPagamento | None = None
    data: date | None = None
    id_animal: int | None = None

class Procedimento(ProcedimentoCreate, table=True):
    id: int | None = Field(default=None, primary_key=True)
    animal: Animal | None = Relationship(back_populates="procedimentos")


engine = create_engine(os.getenv("DATABASE_URL"))
SQLModel.metadata.create_all(engine)
password_hash = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def criar_token(email: str) -> str:
    expira = datetime.now(timezone.utc) + timedelta(minutes=MINUTOS_EXPIRACAO)
    payload = {"sub": email, "exp": expira}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITMO)

def get_session():
    with Session(engine) as session:
        yield session

app = FastAPI(title="Vetsys API", description="API para gerenciamento de tutores e pets", version="1.9.0")
SessionDep = Annotated[Session, Depends(get_session)]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5500", "http://127.0.0.1:5500"],
    allow_methods=["*"],
    allow_headers=["*"],
   )

def get_usuario_atual(token: Annotated[str, Depends(oauth2_scheme)], session: SessionDep) -> Usuario:
    erro = HTTPException(
        status_code=401,
        detail="Não autenticado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITMO])
    except jwt.InvalidTokenError:
        raise erro
    email = payload.get("sub")
    usuario = session.exec(select(Usuario).where(Usuario.email == email)).first()
    if usuario is None:
        raise erro
    return usuario

UsuarioAtual = Annotated[Usuario, Depends(get_usuario_atual)]

def get_funcionario(usuario: UsuarioAtual) -> Usuario:
    if usuario.perfil not in (PerfilUsuario.funcionario, PerfilUsuario.admin):
        raise HTTPException(status_code=403, detail="Acesso restrito a funcionários.")
    return usuario

FuncionarioAtual = Annotated[Usuario, Depends(get_funcionario)]

def get_admin(usuario: UsuarioAtual) -> Usuario:
    if usuario.perfil != PerfilUsuario.admin:
        raise HTTPException(status_code=403, detail="Acesso restrito a administradores.")
    return usuario

AdminAtual = Annotated[Usuario, Depends(get_admin)]

#----------AUTH----------

@app.post("/auth/registro", status_code=201, response_model=UsuarioOut)
def registrar(dados: UsuarioCreate, session: SessionDep):
    usuario = Usuario(nome=dados.nome, email=dados.email, senha_hash=password_hash.hash(dados.senha))
    session.add(usuario)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409, detail="E-mail já cadastrado")
    session.refresh(usuario)
    return usuario

@app.post("/auth/login")
def login(form: Annotated[OAuth2PasswordRequestForm, Depends()], session: SessionDep):
    usuario = session.exec(select(Usuario).where(Usuario.email == form.username)).first()
    if usuario is None or not password_hash.verify(form.password, usuario.senha_hash):
        raise HTTPException(status_code=401, detail="E-mail ou senha incorretos.")
    return {"access_token": criar_token(usuario.email), "token_type": "bearer"}

#----------ADMIN----------

@app.get("/admin/funcionarios", response_model=list[UsuarioAdminOut])
def listar_funcionarios(session: SessionDep, usuario: AdminAtual, skip: int = 0, limit: int = 10):
    return session.exec(select(Usuario).order_by(Usuario.id).where(Usuario.perfil == PerfilUsuario.funcionario).offset(skip).limit(limit)).all()

@app.get("/admin/usuarios", response_model=list[UsuarioAdminOut])
def listar_usuarios(session: SessionDep, usuario: AdminAtual, skip: int = 0, limit: int = 10):
    return session.exec(select(Usuario).order_by(Usuario.id).offset(skip).limit(limit)).all()

@app.patch("/admin/funcionarios/{id_usuario}", response_model=UsuarioAdminOut)
def definir_funcionario(id_usuario: int, session: SessionDep, usuario: AdminAtual):
    alvo = session.get(Usuario, id_usuario)
    if alvo is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    if alvo.id == usuario.id:
        raise HTTPException(status_code=400, detail="Você não pode se rebaixar de admin.")
    alvo.perfil = PerfilUsuario.funcionario
    session.add(alvo)
    session.commit()
    session.refresh(alvo)
    return alvo

@app.patch("/admin/usuarios/{id_usuario}", response_model=UsuarioAdminOut)
def definir_comum(id_usuario: int, session: SessionDep, usuario: AdminAtual):
    alvo = session.get(Usuario, id_usuario)
    if alvo is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    if alvo.id == usuario.id:
        raise HTTPException(status_code=400, detail="Você não pode se rebaixar de admin.")
    alvo.perfil = PerfilUsuario.comum
    session.add(alvo)
    session.commit()
    session.refresh(alvo)
    return alvo

@app.delete("/admin/usuarios/{id_usuario}")
def excluir_usuario(id_usuario: int, session: SessionDep, usuario: AdminAtual):
    alvo = session.get(Usuario, id_usuario)
    if alvo is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    if alvo.id == usuario.id:
        raise HTTPException(status_code=400, detail="Você não pode excluir a si mesmo.")
    session.delete(alvo)
    session.commit()
    return {"mensagem": "Usuário excluido com sucesso."}

#----------PROCEDIMENTOS----------

@app.get("/procedimentos")
def listar_procedimentos(session: SessionDep, usuario: FuncionarioAtual, skip: int = 0, limit: int = 10):
    return session.exec(select(Procedimento).order_by(Procedimento.id).offset(skip).limit(limit)).all()

@app.post("/procedimentos", status_code=201)
def criar_procedimento(dados: ProcedimentoCreate, session: SessionDep, usuario: FuncionarioAtual):
    if session.get(Animal, dados.id_animal) is None:
        raise HTTPException(status_code=404, detail="Animal não encontrado.")
    
    procedimento = Procedimento(**dados.model_dump())
    session.add(procedimento)
    session.commit()
    session.refresh(procedimento)
    return procedimento

@app.put("/procedimentos/{id_procedimento}")
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

@app.patch("/procedimentos/{id_procedimento}")
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

@app.get("/procedimentos/{id_procedimento}")
def buscar_procedimento(id_procedimento: int, session: SessionDep, usuario: FuncionarioAtual):
    procedimento = session.get(Procedimento, id_procedimento)
    if procedimento is None:
        raise HTTPException(status_code=404, detail="Procedimento não encontrado")
    return procedimento

@app.delete("/procedimentos/{id_procedimento}")
def apagar_procedimento(id_procedimento: int, session: SessionDep, usuario: FuncionarioAtual):
    procedimento = session.get(Procedimento, id_procedimento)
    if procedimento is None:
        raise HTTPException(status_code=404, detail="Procedimento não encontrado.")
    session.delete(procedimento)
    session.commit()
    return {"mensagem": "Procedimento apagado com sucesso."}

#----------ANIMAIS----------
@app.get("/animais")
def listar_animais(session: SessionDep, usuario: FuncionarioAtual, skip: int = 0, limit: int = 10):
    return session.exec(select(Animal).order_by(Animal.id).offset(skip).limit(limit)).all()

@app.post("/animais", status_code=201)
def criar_animal(dados: AnimalCreate, session: SessionDep, usuario: FuncionarioAtual):
    if session.get(Tutor, dados.id_tutor) is None:
        raise HTTPException(status_code=404, detail="ID de Tutor inválido ou não encontrado.")
    animal = Animal(**dados.model_dump())
    session.add(animal)
    session.commit()
    session.refresh(animal)
    return animal

@app.put("/animais/{id_animal}")
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

@app.get("/animais/{id_animal}")
def buscar_animal(id_animal: int, session: SessionDep, usuario: FuncionarioAtual):
    animal = session.get(Animal, id_animal)
    if animal is None:
        raise HTTPException(status_code=404, detail="Animal não encontrado")
    return animal

@app.delete("/animais/{id_animal}")
def apagar_animal(id_animal: int, session: SessionDep, usuario: FuncionarioAtual):
    animal = session.get(Animal, id_animal)
    if animal is None:
        raise HTTPException(status_code=404, detail="Animal não encontrado.")
    session.delete(animal)
    session.commit()
    return {"mensagem": "Animal apagado com sucesso."}

@app.get("/animais/{id_animal}/procedimentos")
def buscar_procedimentos_animal(id_animal: int, session: SessionDep, usuario: FuncionarioAtual):
    animal = session.get(Animal, id_animal)
    if animal is None:
        raise HTTPException(status_code=404, detail="ID de animal inválido ou não encontrado")
    procedimentos = session.exec(select(Procedimento).where(Procedimento.id_animal == animal.id).order_by(Procedimento.data)).all()
    return procedimentos

@app.get("/animais/{id_animal}/vacinas")
def buscar_vacinas_animal(id_animal: int, session: SessionDep, usuario: FuncionarioAtual):
    animal = session.get(Animal, id_animal)
    if animal is None:
        raise HTTPException(status_code=404, detail="ID de animal inválido ou não encontrado")
    vacinas = session.exec(select(Procedimento).where(Procedimento.id_animal == animal.id, Procedimento.tipo == TipoProcedimento.vacinacao).order_by(Procedimento.data)).all()
    return vacinas

@app.patch("/animais/{id_animal}")
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

#----------TUTORES----------
@app.post("/tutores", status_code=201)
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

@app.put("/tutores/{id_tutor}")
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

@app.get("/tutores")
def listar_tutores(session: SessionDep, usuario: FuncionarioAtual, skip: int = 0, limit: int = 10):
    return session.exec(select(Tutor).order_by(Tutor.id).offset(skip).limit(limit)).all()

@app.get("/tutores/{id_tutor}")
def buscar_tutor(id_tutor: int, session: SessionDep, usuario: FuncionarioAtual):
    tutor = session.get(Tutor, id_tutor)
    if tutor is None:
        raise HTTPException(status_code=404, detail="Tutor não encontrado")
    return tutor

@app.delete("/tutores/{id_tutor}")
def apagar_tutor(id_tutor: int, session: SessionDep, usuario: FuncionarioAtual):
    tutor = session.get(Tutor, id_tutor)
    if tutor is None:
        raise HTTPException(status_code=404, detail="Tutor não encontrado")
    session.delete(tutor)
    session.commit()
    return {"mensagem": "Tutor, seus animais e procedimentos foram excluídos com sucesso."}

@app.get("/tutores/{id_tutor}/animais")
def buscar_animais_tutor(id_tutor: int, session: SessionDep, usuario: FuncionarioAtual):
    tutor = session.get(Tutor, id_tutor)
    if tutor is None:
        raise HTTPException(status_code=404, detail="Tutor inválido ou não encontrado")
    return tutor.animais

@app.patch("/tutores/{id_tutor}")
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