from sqlmodel import select
from app.security import limiter
from app.models import PerfilUsuario, Usuario

def test_rota_sem_token_da_401(cliente):
    resposta = cliente.get("/tutores")
    assert resposta.status_code == 401

def test_token_invalido_da_401(cliente):
    resposta = cliente.get("/meus/animais", headers={"Authorization": "Bearer abc123"})
    assert resposta.status_code == 401

def test_registro_senha_7_422(cliente):
    resposta = cliente.post("/auth/registro", json={"nome": "Josué Onivaldo", "email": "josueonivaldo@example.com", "senha": "Josue2@"})
    assert resposta.status_code == 422
    
def test_registro_valido_da_201(cliente):
    resposta = cliente.post("/auth/registro", json={"nome": "Josué Onivaldo", "email": "josueonivaldo@example.com", "senha": "Josue292@"})
    dados = resposta.json()
    assert resposta.status_code == 201
    assert "nome" in dados
    assert "senha" not in dados
    assert "senha_hash" not in dados

def test_registro_mesmo_email_409(cliente):
    resposta1 = cliente.post("/auth/registro", json={"nome": "Jefferson Silveira", "email": "jefferson@example.com", "senha": "Jeffer292@"})
    resposta2 = cliente.post("/auth/registro", json={"nome": "Jefferson da Silva", "email": "jefferson@example.com", "senha": "Jeffin939@"})
    assert resposta1.status_code == 201
    assert resposta2.status_code == 409

def test_registro_email_invalido_422(cliente):
    resposta = cliente.post("/auth/registro", json={"nome": "Olivia Palito", "email": "abcd", "senha": "OliviaPalito@"})
    assert resposta.status_code == 422

def test_registro_perfil_admin_201(cliente, session):
    resposta = cliente.post("/auth/registro", json={"nome": "Rodrigo Bisnaga", "email": "rodrigo@example.com", "senha": "Rodrij292@", "perfil": "admin"})
    assert resposta.status_code == 201
    usuario = session.exec(select(Usuario).where(Usuario.email == "rodrigo@example.com")).first()
    assert usuario.perfil == PerfilUsuario.comum

def test_login_certo_200(cliente):
    criacao = cliente.post("/auth/registro", json={"nome": "Rogério Sambodramo", "email": "rogerio@example.com", "senha": "Rogerin292@"})
    resposta = cliente.post("/auth/login", data={"username": "rogerio@example.com", "password": "Rogerin292@" })
    dados = resposta.json()
    assert criacao.status_code == 201
    assert resposta.status_code == 200
    assert "access_token" in dados 
    assert dados["token_type"] == "bearer"

def test_login_senha_errada_401(cliente):
    criacao = cliente.post("/auth/registro", json={"nome": "Silvia Santos", "email": "silvia@example.com", "senha": "Silvia292@"})
    assert criacao.status_code == 201
    login = cliente.post("/auth/login", data={"username": "silvia@example.com", "password": "Silvia292!"})
    assert login.status_code == 401
    dados = login.json()
    assert dados["detail"] == "E-mail ou senha incorretos."

def test_login_email_errado_401(cliente):
    criacao = cliente.post("/auth/registro", json={"nome": "Paula Santos", "email": "paula@example.com", "senha": "Paulinha292@"})
    assert criacao.status_code == 201
    login = cliente.post("/auth/login", data={"username": "paula1@example.com", "password": "Paulinha292@"})
    assert login.status_code == 401
    dados = login.json()
    assert dados["detail"] == "E-mail ou senha incorretos."

def test_6_logins_seguidos_429(cliente):
    limiter.reset()
    limiter.enabled = True
    for _ in range(5):
        cliente.post("/auth/login", data={"username": "paula1@example.com", "password": "Paulinha292@!"})
    sexta = cliente.post("/auth/login", data={"username": "paula1@example.com", "password": "Paulinha292@"})
    assert sexta.status_code == 429

def test_token_de_usuario_excluido_401(cliente, session):
    criacao = cliente.post("/auth/registro", json={"nome": "Lucas Rafael", "email": "lucas@example.com", "senha": "Lusquinha292@"})
    assert criacao.status_code == 201
    usuario = session.exec(select(Usuario).where(Usuario.email == "lucas@example.com")).first()
    login = cliente.post("/auth/login", data={"username": "lucas@example.com", "password": "Lusquinha292@"})
    assert login.status_code == 200
    token = login.json()["access_token"]
    session.delete(usuario)
    session.commit()
    resposta = cliente.get("/meus/animais", headers={"Authorization": "Bearer {}".format(token)})
    assert resposta.status_code == 401
    
