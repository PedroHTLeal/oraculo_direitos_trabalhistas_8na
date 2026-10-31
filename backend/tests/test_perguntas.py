from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_sugestoes_tem_temas_com_perguntas():
    resposta = client.get("/api/sugestoes")
    assert resposta.status_code == 200
    temas = resposta.json()
    assert len(temas) > 0
    for tema in temas:
        assert tema["tema"]
        assert len(tema["perguntas"]) > 0


def test_pergunta_retorna_resposta_no_formato_esperado():
    resposta = client.post("/api/perguntas", json={"texto": "  Quantos dias de férias eu tenho?  "})
    assert resposta.status_code == 200
    dados = resposta.json()
    assert dados["pergunta"] == "Quantos dias de férias eu tenho?"
    assert isinstance(dados["resposta"], str) and dados["resposta"]
    assert isinstance(dados["encontrou"], bool)
    assert isinstance(dados["fontes"], list)


def test_pergunta_sem_informacao_informa_que_nao_encontrou():
    dados = client.post("/api/perguntas", json={"texto": "Pergunta qualquer"}).json()
    assert dados["encontrou"] is False
    assert dados["fontes"] == []


def test_pergunta_muito_curta_e_rejeitada():
    resposta = client.post("/api/perguntas", json={"texto": "oi"})
    assert resposta.status_code == 422


def test_pergunta_so_com_espacos_e_rejeitada():
    resposta = client.post("/api/perguntas", json={"texto": "     "})
    assert resposta.status_code == 422


def test_pergunta_muito_longa_e_rejeitada():
    resposta = client.post("/api/perguntas", json={"texto": "a" * 501})
    assert resposta.status_code == 422
