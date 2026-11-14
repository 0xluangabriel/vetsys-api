from datetime import date
from enum import Enum

from pydantic import EmailStr, ValidationInfo, field_validator
from sqlmodel import Field, Relationship, SQLModel

class UsuarioCreate(SQLModel):
    nome: str = Field(min_length=1, max_length=100)
    email: EmailStr = Field(max_length=150)
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
    tutor = "tutor"

class PerfilEdit(SQLModel):
    perfil: PerfilUsuario

class TutorUserEdit(SQLModel):
    id_tutor: int

class Usuario(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    id_tutor: int | None = Field(default=None, foreign_key="tutor.id", ondelete="SET NULL", unique=True)
    nome: str = Field(max_length=100)
    email: EmailStr = Field(max_length=150, unique=True)
    senha_hash: str = Field(max_length=255)
    perfil: PerfilUsuario = Field(default=PerfilUsuario.comum)

class UsuarioAdminOut(SQLModel):
    id: int
    nome: str
    email: str
    perfil: PerfilUsuario

class TutorCreate(SQLModel):
    nome: str = Field(min_length=1, max_length=100)
    email: EmailStr = Field(max_length=150, unique=True)
    telefone: str = Field(regex=r"^\d+$", max_length=11)
    endereco: str = Field(regex=r"^[\w\s.,ºª'/-]+$", min_length=1, max_length=200)
    numero: str = Field(regex=r"^(\d+[A-Za-z]?|S/N)$", min_length=1, max_length=10)
    cep: str = Field(regex=r"^\d{8}$", max_length=8)
    complemento: str | None = Field(default=None, max_length=15)

class Tutor(TutorCreate, table=True):
    id: int | None = Field(default=None, primary_key=True)
    animais: list["Animal"] = Relationship(back_populates="tutor", cascade_delete=True)

class TutorEdit(SQLModel):
    nome: str | None = Field(default=None, min_length=1, max_length=100)
    email: EmailStr | None = Field(default=None, max_length=150, unique=True)
    telefone: str | None = Field(default=None, regex=r"^\d+$", max_length=11)
    endereco: str | None = Field(default=None, regex=r"^[\w\s.,ºª'/-]+$", min_length=1, max_length=200)
    numero: str | None = Field(regex=r"^(\d+[A-Za-z]?|S/N)$", default=None, min_length=1, max_length=10)
    cep: str | None = Field(default=None, regex=r"^\d{8}$")
    complemento: str | None = Field(default=None, max_length=15)

    @field_validator("endereco", "cep", "numero")
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
