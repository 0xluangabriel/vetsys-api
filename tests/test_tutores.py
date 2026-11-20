from sqlmodel import select
from app.models import Tutor, Animal, Procedimento, TipoProcedimento, FormaPagamento
from datetime import date

def test_criar_tutor_sem_complemento_201(cliente, headers_funcionario):
    requisicao = cliente.post("/tutores", headers=headers_funcionario, json={"nome": "José Olimpio", "email": "joseolimpio@example.com", "telefone": "31999999999", "endereco": "Rua Exemplo, Exemplo", "numero": "000", "cep": "00000000"})
    assert requisicao.status_code == 201
    json = requisicao.json()
    assert json["complemento"] is None

def test_patch_so_com_telefone_200(session, cliente, headers_funcionario):
    criacao = cliente.post("/tutores", headers=headers_funcionario, json={"nome": "José Olimpio", "email": "joseolimpio@example.com", "telefone": "31999999999", "endereco": "Rua Exemplo, Exemplo", "numero": "000", "cep": "00000000", "complemento": None})
    assert criacao.status_code == 201
    tutorid = session.exec(select(Tutor.id).where(Tutor.email == "joseolimpio@example.com")).first()
    requisicao = cliente.patch("/tutores/{}".format(tutorid), headers=headers_funcionario, json={"telefone": "31999999900"})
    assert requisicao.status_code == 200
    telefone = session.exec(select(Tutor.telefone).where(Tutor.email == "joseolimpio@example.com")).first()
    assert telefone == "31999999900"
    endereco = session.exec(select(Tutor.endereco).where(Tutor.email == "joseolimpio@example.com")).first()
    assert endereco == "Rua Exemplo, Exemplo"

def test_apagar_tutor_cascata(session, cliente, headers_funcionario):
    tutor = Tutor(nome="José Olimpio", email="joseolimpio@example.com", telefone="31999999999", endereco="Rua Exemplo, Exemplo", numero="000", complemento="Casa", cep="00000000")
    session.add(tutor)
    session.commit()
    tutorid = tutor.id
    animal = Animal(id_tutor=tutor.id, nome="Rodolfo", especie="Porco", raca="Caipira", sexo="M", idade=4, peso=10.75)
    session.add(animal)
    session.commit()
    animalid = animal.id
    procedimento = Procedimento(id_animal=animal.id, nome="Consulta", descricao="Consulta de rotina", preco=100, tipo=TipoProcedimento.consulta, forma_pagamento=FormaPagamento.dinheiro, data=date.today())
    session.add(procedimento)
    session.commit()
    procedimentoid = procedimento.id
    requisicao = cliente.delete("/tutores/{}".format(tutor.id), headers=headers_funcionario)
    assert requisicao.status_code == 200
    procapagou = session.get(Procedimento, procedimentoid)
    assert procapagou is None
    animalapagou = session.get(Animal, animalid)
    assert animalapagou is None
    tutorapagou = session.get(Tutor, tutorid)
    assert tutorapagou is None