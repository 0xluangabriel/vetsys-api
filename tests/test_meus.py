from sqlmodel import select
from datetime import date
from app.security import limiter
from app.models import Tutor, Animal, Procedimento, TipoProcedimento, FormaPagamento

def test_idor_meus_animais(cliente, session, headers_tutor):
    email = "marcoaurelio@example.com"
    id_tutor = session.exec(select(Tutor.id).where(Tutor.email == "marianacosta@example.com")).first()
    tutor_b = Tutor(nome="Marco Aurelio", email=email, telefone="31999999999", endereco="Rua Exemplo", numero="000", cep="00000000", complemento="Exemplo")
    session.add(tutor_b)
    session.commit()
    animalA = Animal(id_tutor=id_tutor, nome="Animal Exemplo A", especie="Exemplo A", raca="Exemplo A", sexo="M", idade=3, peso=1)
    session.add(animalA)
    session.commit()
    animalB = Animal(id_tutor=tutor_b.id, nome="Animal Exemplo B", especie="Exemplo N", raca="Exemplo B", sexo="M", idade=3, peso=1)
    session.add(animalB)
    session.commit()
    requisicao = cliente.get("/meus/animais", headers=headers_tutor)
    resultadoa = requisicao.json()
    assert requisicao.status_code == 200
    assert len(resultadoa) == 1
    assert resultadoa[0]["nome"] == "Animal Exemplo A"

def test_idor_meus_procedimentos(cliente, session, headers_tutor):
    email = "marcossantos@example.com"
    id_tutor = session.exec(select(Tutor.id).where(Tutor.email == "marianacosta@example.com")).first()
    tutor_b = Tutor(nome="Marcos Santos", email=email, telefone="31999999999", endereco="Rua Exemplo", numero="000", cep="00000000", complemento="Exemplo")
    session.add(tutor_b)
    session.commit()
    animalA = Animal(id_tutor=id_tutor, nome="Animal Exemplo A", especie="Exemplo A", raca="Exemplo A", sexo="M", idade=3, peso=1)
    session.add(animalA)
    session.commit()
    animalB = Animal(id_tutor=tutor_b.id, nome="Animal Exemplo B", especie="Exemplo N", raca="Exemplo B", sexo="M", idade=3, peso=1)
    session.add(animalB)
    session.commit()
    procedimentoA = Procedimento(id_animal=animalA.id, nome="Vacina Exemplo A", descricao="Exemplo A", preco=120, tipo=TipoProcedimento.vacinacao, forma_pagamento=FormaPagamento.pix, data=date.today())
    session.add(procedimentoA)
    session.commit()
    procedimentoB = Procedimento(id_animal=animalB.id, nome="Vacina Exemplo B", descricao="Exemplo B", preco=120, tipo=TipoProcedimento.vacinacao, forma_pagamento=FormaPagamento.pix, data=date.today())
    session.add(procedimentoB)
    session.commit()
    requisicao = cliente.get("/meus/procedimentos", headers=headers_tutor)
    resultadoa = requisicao.json()
    assert requisicao.status_code == 200
    assert len(resultadoa) == 1
    assert resultadoa[0]["nome"] == "Vacina Exemplo A"


