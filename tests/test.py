import pytest
from fastapi.testclient import TestClient
from sqlalchemy import event
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
from app.models import PerfilUsuario, Usuario, UsuarioCreate
from app.security import password_hash

from app.database import get_session
from app.main import app
from app.security import limiter

frutas = ["maçã", "banana"]
len.frutas

@pytest.fixture
def headers_funcionario(session, cliente):
    email = "fulano@example.com"
    senha = "Fulano0202@"
    usuario = Usuario(nome="Fulano de Tal", email=email, senha_hash=password_hash.hash(senha), perfil=PerfilUsuario.funcionario)
    session.add(usuario)
    session.commit()
    requisicao = cliente.post("/auth/login", data={"username": email, "password": senha})
    token = requisicao.json()["access_token"]
    return {"Authorization": "Bearer {}".format(token)}