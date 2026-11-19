import pytest
from fastapi.testclient import TestClient
from sqlalchemy import event
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
from app.models import PerfilUsuario, Usuario, Tutor
from app.security import password_hash

from app.database import get_session
from app.main import app
from app.security import limiter


@pytest.fixture
def session():
    # "sqlite://" sem nome de arquivo = banco em memória
    # StaticPool = todas as conexões usam o mesmo banco (senão cada uma veria um banco vazio)
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # O SQLite vem com as chaves estrangeiras DESLIGADAS.
    # Sem isso, CASCADE e SET NULL não funcionam nos testes.
    @event.listens_for(engine, "connect")
    def ligar_fks(conexao, _):
        cursor = conexao.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session   # o teste roda aqui; depois disso o banco some


@pytest.fixture
def cliente(session):
    def get_session_teste():
        yield session

    app.dependency_overrides[get_session] = get_session_teste
    limiter.enabled = False

    yield TestClient(app)

    # limpeza: devolve o app ao normal para não vazar para outros testes
    app.dependency_overrides.clear()
    limiter.enabled = True

@pytest.fixture
def headers_funcionario(session, cliente):
    email = "joseromero@example.com"
    senha = "JoseRomero22@"
    funcionario = Usuario(nome="José Romero", email=email, senha_hash=password_hash.hash(senha), perfil=PerfilUsuario.funcionario)
    session.add(funcionario)
    session.commit()
    login = cliente.post("/auth/login", data={"username": email, "password": senha})
    token = login.json()["access_token"]
    return {"Authorization": "Bearer {}".format(token)}

@pytest.fixture
def headers_admin(session, cliente):
    email = "flavionolasco@example.com"
    senha = "FlavioNolasco22@"
    admin = Usuario(nome="Flavio Nolasco", email=email, senha_hash=password_hash.hash(senha), perfil=PerfilUsuario.admin)
    session.add(admin)
    session.commit()
    login = cliente.post("/auth/login", data={"username": email, "password": senha})
    token = login.json()["access_token"]
    return {"Authorization": "Bearer {}".format(token)}

@pytest.fixture
def headers_comum(session, cliente):
    email = "rodrigosilvo@example.com"
    senha = "RodrigoSilvo22@"
    comum = Usuario(nome="Rodrigo Silvo", email=email, senha_hash=password_hash.hash(senha), perfil=PerfilUsuario.comum)
    session.add(comum)
    session.commit()
    login = cliente.post("/auth/login", data={"username": email, "password": senha})
    token = login.json()["access_token"]
    return {"Authorization": "Bearer {}".format(token)}

@pytest.fixture
def headers_tutor(session, cliente):
    email = "marianacosta@example.com"
    senha = "MarianaCosta22@"
    tutor_db = Tutor(nome="Mariana Costa", email=email, telefone="31999999999", endereco="Rua Exemplo", numero="000", cep="00000000", complemento="Exemplo")
    session.add(tutor_db)
    session.commit()
    tutor = Usuario(id_tutor=tutor_db.id, nome="Mariana Costa", email=email, senha_hash=password_hash.hash(senha), perfil=PerfilUsuario.tutor)
    session.add(tutor)
    session.commit()
    login = cliente.post("/auth/login", data={"username": email, "password": senha})
    token = login.json()["access_token"]
    return {"Authorization": "Bearer {}".format(token)}