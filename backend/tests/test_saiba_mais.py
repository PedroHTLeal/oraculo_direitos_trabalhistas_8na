def perguntar(client):
    return client.post("/api/perguntas", json={"texto": "Quantos dias de férias eu tenho?"}).json()["id"]


def test_envia_resposta_links_e_videos_pelo_whatsapp(client, falsos):
    repositorio, ia, whatsapp = falsos
    pergunta_id = perguntar(client)

    resposta = client.post(
        "/api/saiba-mais",
        json={"pergunta_id": pergunta_id, "telefone": "(51) 99999-8888", "consentimento": True},
    )

    assert resposta.status_code == 202
    solicitacao_id = resposta.json()["id"]
    telefone, texto = whatsapp.enviadas[0]
    assert telefone == "+5551999998888"
    assert "Você tem direito a 30 dias." in texto
    assert "https://www.gov.br/ferias" in texto
    assert "https://www.youtube.com/watch?v=abc" in texto
    assert ia.tema_pesquisado == "Férias"
    assert client.get(f"/api/saiba-mais/{solicitacao_id}").json()["status"] == "enviado"


def test_sem_consentimento_nao_envia(client, falsos):
    _, _, whatsapp = falsos
    pergunta_id = perguntar(client)

    resposta = client.post(
        "/api/saiba-mais",
        json={"pergunta_id": pergunta_id, "telefone": "51999998888", "consentimento": False},
    )

    assert resposta.status_code == 422
    assert whatsapp.enviadas == []


def test_telefone_invalido_e_rejeitado(client, falsos):
    pergunta_id = perguntar(client)

    resposta = client.post(
        "/api/saiba-mais",
        json={"pergunta_id": pergunta_id, "telefone": "12345", "consentimento": True},
    )

    assert resposta.status_code == 422
    assert "DDD" in resposta.json()["detail"]


def test_pergunta_inexistente(client, falsos):
    resposta = client.post(
        "/api/saiba-mais",
        json={"pergunta_id": "nao-existe", "telefone": "51999998888", "consentimento": True},
    )
    assert resposta.status_code == 404


def test_falha_na_pesquisa_marca_pedido_com_erro(client, falsos):
    _, ia, whatsapp = falsos
    ia.falhar_materiais = True
    pergunta_id = perguntar(client)

    solicitacao_id = client.post(
        "/api/saiba-mais",
        json={"pergunta_id": pergunta_id, "telefone": "51999998888", "consentimento": True},
    ).json()["id"]

    assert whatsapp.enviadas == []
    assert client.get(f"/api/saiba-mais/{solicitacao_id}").json()["status"] == "erro"


def test_instrucoes_do_sandbox(client, falsos):
    dados = client.get("/api/whatsapp").json()
    assert dados == {"numero": "+14155238886", "codigo": "join teste-oraculo"}
