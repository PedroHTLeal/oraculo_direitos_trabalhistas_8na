INSCRICAO = {"tema_id": 1, "telefone": "(51) 99999-8888", "consentimento": True}


def test_usuario_acompanha_e_deixa_de_acompanhar_um_tema(client, falsos, entrar):
    cabecalho = entrar("usuario")

    criada = client.post("/api/inscricoes", json=INSCRICAO, headers=cabecalho)
    assert criada.status_code == 201
    assert criada.json()["tema"] == "Férias"
    assert criada.json()["telefone"] == "+5551999998888"

    assert len(client.get("/api/inscricoes", headers=cabecalho).json()) == 1
    assert client.delete(f"/api/inscricoes/{criada.json()['id']}", headers=cabecalho).status_code == 204
    assert client.get("/api/inscricoes", headers=cabecalho).json() == []


def test_inscricao_repetida(client, falsos, entrar):
    cabecalho = entrar("usuario")
    client.post("/api/inscricoes", json=INSCRICAO, headers=cabecalho)

    resposta = client.post("/api/inscricoes", json=INSCRICAO, headers=cabecalho)

    assert resposta.status_code == 409


def test_validacoes_da_inscricao(client, falsos, entrar):
    cabecalho = entrar("usuario")

    sem_consentimento = client.post("/api/inscricoes", json={**INSCRICAO, "consentimento": False}, headers=cabecalho)
    telefone_invalido = client.post("/api/inscricoes", json={**INSCRICAO, "telefone": "123"}, headers=cabecalho)

    assert sem_consentimento.status_code == telefone_invalido.status_code == 422
    assert "DDD" in telefone_invalido.json()["detail"]


def test_usuario_nao_exclui_inscricao_de_outro(client, falsos, entrar):
    criada = client.post("/api/inscricoes", json=INSCRICAO, headers=entrar("usuario")).json()

    resposta = client.delete(f"/api/inscricoes/{criada['id']}", headers=entrar("usuario"))

    assert resposta.status_code == 404
