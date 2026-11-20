from sqlmodel import select
from app.models import Tutor, Animal, Procedimento, TipoProcedimento, FormaPagamento
from datetime import date

def test_apagar_tutor_cascata(session, cliente, headers_funcionario):
    tutor = Tutor(nome="José Olimpio", email="joseolimpio@example.com", telefone="31999999999", endereco="Rua Exemplo, Exemplo", numero="000", complemento="Casa", cep="00000000")
    session.add(tutor)
    session.commit()
    animal = Animal(id_tutor=tutor.id, nome="Rodolfo", especie="Porco", raca="Caipira", sexo="M", idade=4, peso=10.75)
    session.add(animal)
    session.commit()
    animalid = animal.id
    procedimento = Procedimento(id_animal=animal.id, nome="Consulta", descricao="Consulta de rotina", preco=100, tipo=TipoProcedimento.consulta, forma_pagamento=FormaPagamento.dinheiro, data=date.today())
    session.add(procedimento)
    session.commit()
    procedimentoid = procedimento.id
    requisicao = cliente.delete("/animais/{}".format(animal.id), headers=headers_funcionario)
    assert requisicao.status_code == 200
    animalapagou = session.get(Animal, animalid)
    assert animalapagou is None
    procapagou = session.get(Procedimento, procedimentoid)
    assert procapagou is None
    