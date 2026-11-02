def perguntar(client):
    return client.post("/api/perguntas", json={"texto": "Quantos dias de férias eu tenho?"}).json()["id"]


def test_envia_resposta_links_e_videos_para_o_whatsapp_da_conta(client, falsos, entrar):
    repositorio, ia, whatsapp = falsos
    cabecalho = entrar("usuario", login="+5551999998888")
    pergunta_id = perguntar(client)

    resposta = client.post("/api/saiba-mais", json={"pergunta_id": pergunta_id}, headers=cabecalho)

    assert resposta.status_code == 202
    solicitacao_id = resposta.json()["id"]
    telefone, texto = whatsapp.enviadas[0]
    assert telefone == "+5551999998888"
    assert "Você tem direito a 30 dias." in texto
    assert "https://www.gov.br/ferias" in texto
    assert "https://www.youtube.com/watch?v=abc" in texto
    assert ia.tema_pesquisado == "Férias"
    assert client.get(f"/api/saiba-mais/{solicitacao_id}").json()["status"] == "enviado"


def test_saiba_mais_exige_login(client, falsos):
    _, _, whatsapp = falsos

    resposta = client.post("/api/saiba-mais", json={"pergunta_id": perguntar(client)})

    assert resposta.status_code == 401
    assert whatsapp.enviadas == []


def test_conta_sem_telefone_nao_recebe(client, falsos, entrar):
    resposta = client.post("/api/saiba-mais", json={"pergunta_id": perguntar(client)}, headers=entrar("curador"))

    assert resposta.status_code == 422
    assert "telefone" in resposta.json()["detail"]


def test_pergunta_inexistente(client, falsos, entrar):
    resposta = client.post("/api/saiba-mais", json={"pergunta_id": "nao-existe"}, headers=entrar("usuario"))
    assert resposta.status_code == 404


def test_falha_na_pesquisa_marca_pedido_com_erro(client, falsos, entrar):
    _, ia, whatsapp = falsos
    ia.falhar_materiais = True

    solicitacao_id = client.post(
        "/api/saiba-mais", json={"pergunta_id": perguntar(client)}, headers=entrar("usuario")
    ).json()["id"]

    assert whatsapp.enviadas == []
    assert client.get(f"/api/saiba-mais/{solicitacao_id}").json()["status"] == "erro"


def test_instrucoes_do_sandbox(client, falsos):
    dados = client.get("/api/whatsapp").json()
    assert dados == {"numero": "+14155238886", "codigo": "join teste-oraculo"}
