def test_rota_funcionario_200(cliente, headers_funcionario):
    resposta = cliente.get("/tutores", headers=headers_funcionario)
    assert resposta.status_code == 200