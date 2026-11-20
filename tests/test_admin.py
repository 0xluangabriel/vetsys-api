from sqlmodel import select
from app.security import limiter
from app.models import PerfilUsuario, Usuario, Tutor
from app.security import password_hash

def test_admin_usuarios_ncontem_senhahash(cliente, headers_admin):
    requisicao = cliente.get("/admin/usuarios", headers=headers_admin)
    usuarios = requisicao.json()
    for usuario in usuarios:
        assert "senha_hash" not in usuario

def test_segunda_conta_mesmo_tutor_409(session, cliente, headers_admin):
    conta1 = cliente.post("/auth/registro", json={"nome": "Lucas Teodoro", "email": "lucasteodoro@example.com", "senha": "Lusquinha292@"})
    assert conta1.status_code == 201
    conta2 = cliente.post("/auth/registro", json={"nome": "Rafael Barcelos", "email": "rafaelbarcelos@example.com", "senha": "Rafael292@"})
    assert conta2.status_code == 201
    email = "lucasteodoromail@example.com"
    tutor = Tutor(nome="Lucas Teodoro", email=email, telefone="31999999999", endereco="Rua Exemplo", numero="000", cep="00000000", complemento="Exemplo")
    session.add(tutor)
    session.commit()
    id_usuario1 = session.exec(select(Usuario.id).where(Usuario.email == "lucasteodoro@example.com")).first()
    id_usuario2 = session.exec(select(Usuario.id).where(Usuario.email == "rafaelbarcelos@example.com")).first()
    id_tutor = session.exec(select(Tutor.id).where(Tutor.email == "lucasteodoromail@example.com")).first()
    requisicaoA = cliente.patch("/admin/usuarios/{}/tutor".format(id_usuario1), headers=headers_admin, json={"id_tutor": id_tutor})
    assert requisicaoA.status_code == 200
    requisicaoB = cliente.patch("/admin/usuarios/{}/tutor".format(id_usuario2), headers=headers_admin, json={"id_tutor": id_tutor})
    assert requisicaoB.status_code == 409

def test_admin_nao_se_rebaixa_400(session, cliente, headers_admin):
    id_usuario = session.exec(select(Usuario.id).where(Usuario.email == "flavionolasco@example.com")).first()
    requisicao = cliente.patch("/admin/usuarios/{}".format(id_usuario), headers=headers_admin)
    assert requisicao.status_code == 400

def test_rebaixar_libera_tutor_para_outra_conta_200(session, cliente, headers_admin):
    usuario1 = Usuario(nome="Lucas Teodoro", email="lucasteodoro@example.com", senha_hash=password_hash.hash("Lusquinha292@"), perfil=PerfilUsuario.tutor)
    usuario2 = Usuario(nome="Rafael Barcelos", email="rafaelbarcelos@example.com", senha_hash=password_hash.hash("Rafael292@"), perfil=PerfilUsuario.tutor)
    session.add(usuario1)
    session.add(usuario2)
    email = "lucasteodoromail@example.com"
    tutor = Tutor(nome="Lucas Teodoro", email=email, telefone="31999999999", endereco="Rua Exemplo", numero="000", cep="00000000", complemento="Exemplo")
    session.add(tutor)
    session.commit()
    id_tutor = session.exec(select(Tutor.id).where(Tutor.email == "lucasteodoromail@example.com")).first()
    vincular = cliente.patch("/admin/usuarios/{}/tutor".format(usuario1.id), headers=headers_admin, json={"id_tutor": id_tutor})
    assert vincular.status_code == 200
    rebaixar = cliente.patch("/admin/usuarios/{}".format(usuario1.id), headers=headers_admin)
    session.refresh(usuario1)
    assert rebaixar.status_code == 200
    assert usuario1.id_tutor is None
    vincular2 = cliente.patch("/admin/usuarios/{}/tutor".format(usuario2.id), headers=headers_admin, json={"id_tutor": id_tutor})
    assert vincular2.status_code == 200