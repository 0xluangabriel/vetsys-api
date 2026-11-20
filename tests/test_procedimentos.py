from datetime import date, timedelta
from app.models import Tutor, Animal, Procedimento, TipoProcedimento, FormaPagamento

def test_post_data_passada_422(session, cliente, headers_funcionario):
    tutor = Tutor(nome="Ana Souza", email="anasouza@example.com", telefone="31999999999", endereco="Rua Exemplo, Exemplo", numero="000", complemento="Casa", cep="00000000")
    session.add(tutor)
    session.commit()
    animal = Animal(id_tutor=tutor.id, nome="Tobias", especie="Cachorro", raca="SRD", sexo="M", idade=2, peso=12.5)
    session.add(animal)
    session.commit()
    ontem = date.today() - timedelta(days=1)
    requisicao = cliente.post("/procedimentos", headers=headers_funcionario, json={"id_animal": animal.id, "nome": "Consulta", "descricao": "Consulta de rotina", "preco": 80, "tipo": "Consulta", "data": ontem.isoformat()})
    assert requisicao.status_code == 422

def test_put_data_passada_422(session, cliente, headers_funcionario):
    tutor = Tutor(nome="Ana Souza", email="anasouza@example.com", telefone="31999999999", endereco="Rua Exemplo, Exemplo", numero="000", complemento="Casa", cep="00000000")
    session.add(tutor)
    session.commit()
    animal = Animal(id_tutor=tutor.id, nome="Tobias", especie="Cachorro", raca="SRD", sexo="M", idade=2, peso=12.5)
    session.add(animal)
    session.commit()
    amanha = date.today() + timedelta(days=1)
    ontem = date.today() - timedelta(days=1)
    criacao = cliente.post("/procedimentos", headers=headers_funcionario, json={"id_animal": animal.id, "nome": "Consulta", "descricao": "Consulta de rotina", "preco": 80, "tipo": "Consulta", "data": amanha.isoformat()})
    assert criacao.status_code == 201
    procedimentoid = criacao.json()["id"]
    requisicao = cliente.put("/procedimentos/{}".format(procedimentoid), headers=headers_funcionario, json={"id_animal": animal.id, "nome": "Consulta", "descricao": "Consulta de rotina", "preco": 80, "tipo": "Consulta", "data": ontem.isoformat()})
    assert requisicao.status_code == 422

def test_patch_preco_procedimento_passado_200(session, cliente, headers_funcionario):
    tutor = Tutor(nome="Ana Souza", email="anasouza@example.com", telefone="31999999999", endereco="Rua Exemplo, Exemplo", numero="000", complemento="Casa", cep="00000000")
    session.add(tutor)
    session.commit()
    animal = Animal(id_tutor=tutor.id, nome="Tobias", especie="Cachorro", raca="SRD", sexo="M", idade=2, peso=12.5)
    session.add(animal)
    session.commit()
    procedimento = Procedimento(id_animal=animal.id, nome="Vacina", descricao="Vacina V10", preco=100, tipo=TipoProcedimento.vacinacao, forma_pagamento=FormaPagamento.pix, data=date.today() - timedelta(days=30))
    session.add(procedimento)
    session.commit()
    procedimentoid = procedimento.id
    requisicao = cliente.patch("/procedimentos/{}".format(procedimentoid), headers=headers_funcionario, json={"preco": 150})
    assert requisicao.status_code == 200
    session.refresh(procedimento)
    assert procedimento.preco == 150