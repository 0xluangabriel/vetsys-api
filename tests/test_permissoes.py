from sqlmodel import select
from app.models import Tutor

def test_funcionario_rota_tutores_200(cliente, headers_funcionario):
    resposta = cliente.get("/tutores", headers=headers_funcionario)
    assert resposta.status_code == 200

def test_comum_rota_tutores_403(cliente, headers_comum):
    resposta = cliente.get("/tutores", headers=headers_comum)
    assert resposta.status_code == 403

def test_tutor_rota_tutores_403(cliente, headers_tutor):
    resposta = cliente.get("/tutores", headers=headers_tutor)
    assert resposta.status_code == 403

def test_funcionario_rota_admin_403(cliente, headers_funcionario):
    resposta = cliente.get("/admin/usuarios", headers=headers_funcionario)
    assert resposta.status_code == 403

def test_admin_rota_admin_200(cliente, headers_admin):
    resposta = cliente.get("/admin/usuarios", headers=headers_admin)
    assert resposta.status_code == 200

def test_funcionario_rota_tutor_meus_403(cliente, headers_funcionario):
    resposta = cliente.get("/meus/animais", headers=headers_funcionario)
    assert resposta.status_code == 403

def test_tutor_sem_vinculo_rota_tutor_403(cliente, session, headers_tutor):
    tutor = session.exec(select(Tutor).where(Tutor.email == "marianacosta@example.com")).first()
    session.delete(tutor)
    session.commit()
    resposta = cliente.get("/meus/animais", headers=headers_tutor)
    assert resposta.status_code == 403