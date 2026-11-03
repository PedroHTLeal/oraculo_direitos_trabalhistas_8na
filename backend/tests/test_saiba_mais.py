def perguntar(client):
    return client.post("/api/perguntas", json={"texto": "Quantos dias de férias eu tenho?"}).json()["id"]


def pedido(pergunta_id, **campos):
    return {"pergunta_id": pergunta_id, "nome": "Maria", "email": "maria@exemplo.com.br", "consentimento": True, **campos}


def test_envia_resposta_sites_e_videos_para_o_email_informado(client, falsos):
    repositorio, _, email = falsos

    resposta = client.post("/api/saiba-mais", json=pedido(perguntar(client)))

    assert resposta.status_code == 202
    solicitacao_id = resposta.json()["id"]
    destinatario, conteudo = email.enviados[0]
    assert destinatario == "maria@exemplo.com.br"
    assert "Olá, Maria!" in conteudo["texto"]
    # Materiais escolhidos pela equipe para "Férias" + a página da cartilha do tema
    for parte in ("Você tem direito a 30 dias.", "https://www.exemplo.com.br/ferias", "https://www.trt4.jus.br/portais/trt4/ferias", "https://www.youtube.com/watch?v=abc"):
        assert parte in conteudo["texto"] and parte in conteudo["html"]
    assert client.get(f"/api/saiba-mais/{solicitacao_id}").json()["status"] == "enviado"
    assert repositorio.historico[-1]["acao"] == "pedir_conteudo"
    assert repositorio.historico[-1]["usuario_nome"] == "Maria"


def test_saiba_mais_nao_exige_login(client, falsos):
    resposta = client.post("/api/saiba-mais", json=pedido(perguntar(client)))
    assert resposta.status_code == 202


def test_exige_autorizacao_do_envio(client, falsos):
    _, _, email = falsos

    resposta = client.post("/api/saiba-mais", json=pedido(perguntar(client), consentimento=False))

    assert resposta.status_code == 422
    assert resposta.json()["detail"] == "É preciso autorizar o envio do conteúdo para o seu e-mail."
    assert email.enviados == []


def test_rejeita_email_invalido_e_nome_curto(client, falsos):
    resposta = client.post("/api/saiba-mais", json=pedido(perguntar(client), email="maria", nome="M"))

    assert resposta.status_code == 422
    erros = resposta.json()["erros"]
    assert "Informe um e-mail válido, por exemplo nome@exemplo.com." in erros
    assert "O campo nome precisa ter pelo menos 2 caracteres." in erros


def test_limita_pedidos_por_hora_para_o_mesmo_email(client, falsos):
    pergunta_id = perguntar(client)
    for _ in range(5):
        assert client.post("/api/saiba-mais", json=pedido(pergunta_id)).status_code == 202

    resposta = client.post("/api/saiba-mais", json=pedido(pergunta_id, email="MARIA@exemplo.com.br"))

    assert resposta.status_code == 429


def test_pergunta_inexistente(client, falsos):
    resposta = client.post("/api/saiba-mais", json=pedido("nao-existe"))
    assert resposta.status_code == 404


def test_falha_no_envio_marca_pedido_com_erro(client, falsos):
    _, _, email = falsos

    def falhar(destinatario, conteudo):
        raise RuntimeError("Gmail fora do ar")

    email.enviar = falhar
    solicitacao_id = client.post("/api/saiba-mais", json=pedido(perguntar(client))).json()["id"]

    assert client.get(f"/api/saiba-mais/{solicitacao_id}").json()["status"] == "erro"
