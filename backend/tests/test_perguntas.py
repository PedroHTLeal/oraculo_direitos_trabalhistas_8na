def test_sugestoes_tem_temas_com_perguntas(client):
    resposta = client.get("/api/sugestoes")
    assert resposta.status_code == 200
    temas = resposta.json()
    assert len(temas) > 0
    for tema in temas:
        assert tema["tema"]
        assert len(tema["perguntas"]) > 0


def test_pergunta_responde_com_base_nos_trechos(client, falsos):
    repositorio, _, _ = falsos
    dados = client.post("/api/perguntas", json={"texto": "  Quantos dias de férias eu tenho?  "}).json()

    assert dados["pergunta"] == "Quantos dias de férias eu tenho?"
    assert dados["encontrou"] is True
    assert dados["resposta"] == "Você tem direito a 30 dias."
    assert dados["id"] in repositorio.perguntas


def test_fontes_so_incluem_trechos_encontrados_na_busca(client, falsos):
    # A IA citou o trecho 99, que não veio da busca: ele deve ser ignorado
    repositorio, _, _ = falsos
    dados = client.post("/api/perguntas", json={"texto": "Quantos dias de férias?"}).json()

    assert [f["titulo"] for f in dados["fontes"]] == ["Férias · Visão geral"]
    assert dados["fontes"][0]["url"] == "https://www.trt4.jus.br/portais/trt4/ferias"
    assert repositorio.perguntas[dados["id"]]["trechos_ids"] == [10]


def test_sem_trechos_informa_que_nao_encontrou(client, falsos):
    repositorio, _, _ = falsos
    repositorio.trechos = []
    dados = client.post("/api/perguntas", json={"texto": "Qual a capital da França?"}).json()

    assert dados["encontrou"] is False
    assert dados["fontes"] == []
    assert "Não encontrei" in dados["resposta"]


def test_ia_sem_informacao_suficiente_nao_mostra_fontes(client, falsos):
    _, ia, _ = falsos
    ia.resultado = {"encontrou": False, "resposta": "A cartilha não trata disso.", "trechos_usados": [10]}
    dados = client.post("/api/perguntas", json={"texto": "Posso levar meu cachorro?"}).json()

    assert dados["encontrou"] is False
    assert dados["fontes"] == []


def test_recusa_da_ia_vira_resposta_sem_informacao(client, falsos):
    _, ia, _ = falsos
    ia.recusar = True
    dados = client.post("/api/perguntas", json={"texto": "Pergunta qualquer"}).json()

    assert dados["encontrou"] is False


def test_pergunta_muito_curta_e_rejeitada(client, falsos):
    assert client.post("/api/perguntas", json={"texto": "oi"}).status_code == 422


def test_pergunta_so_com_espacos_e_rejeitada(client, falsos):
    assert client.post("/api/perguntas", json={"texto": "     "}).status_code == 422


def test_pergunta_muito_longa_e_rejeitada(client, falsos):
    assert client.post("/api/perguntas", json={"texto": "a" * 501}).status_code == 422
