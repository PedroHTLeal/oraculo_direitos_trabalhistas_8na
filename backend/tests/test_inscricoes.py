def test_usuario_acompanha_tema_no_email_da_conta(client, falsos, entrar):
    cabecalho = entrar("usuario", login="maria@exemplo.com.br")

    criada = client.post("/api/inscricoes", json={"tema_id": 1}, headers=cabecalho)
    assert criada.status_code == 201
    assert criada.json()["tema"] == "Férias"
    assert criada.json()["email"] == "maria@exemplo.com.br"

    assert len(client.get("/api/inscricoes", headers=cabecalho).json()) == 1
    assert client.delete(f"/api/inscricoes/{criada.json()['id']}", headers=cabecalho).status_code == 204
    assert client.get("/api/inscricoes", headers=cabecalho).json() == []


def test_inscricao_repetida(client, falsos, entrar):
    cabecalho = entrar("usuario")
    client.post("/api/inscricoes", json={"tema_id": 1}, headers=cabecalho)

    resposta = client.post("/api/inscricoes", json={"tema_id": 1}, headers=cabecalho)

    assert resposta.status_code == 409


def test_validacoes_da_inscricao(client, falsos, entrar):
    tema_invalido = client.post("/api/inscricoes", json={"tema_id": 99}, headers=entrar("usuario"))

    assert tema_invalido.status_code == 422
    assert tema_invalido.json()["detail"] == "Escolha um tema válido."


def test_usuario_nao_exclui_inscricao_de_outro(client, falsos, entrar):
    criada = client.post("/api/inscricoes", json={"tema_id": 1}, headers=entrar("usuario")).json()

    resposta = client.delete(f"/api/inscricoes/{criada['id']}", headers=entrar("usuario"))

    assert resposta.status_code == 404
