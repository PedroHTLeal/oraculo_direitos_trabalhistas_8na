import pytest

from app.ia import formatar_trechos
from app.repositorio import diversificar


def test_formata_trechos_com_numero_para_a_ia():
    texto = formatar_trechos([{"id": 7, "tema": "Férias", "secao": "Visão geral", "texto": "30 dias"}])
    assert '<trecho numero="7" tema="Férias" secao="Visão geral">' in texto


def test_diversifica_trechos_por_tema():
    trechos = [{"id": i, "tema": "Férias"} for i in range(5)] + [
        {"id": 10, "tema": "Contrato de Estágio"},
        {"id": 11, "tema": "Rescisão"},
    ]
    escolhidos = diversificar(trechos, limite=6)

    assert [t["id"] for t in escolhidos] == [0, 1, 2, 10, 11]


def test_repete_a_operacao_quando_a_conexao_cai():
    import httpx

    from app.repositorio import _repetir_se_a_conexao_cair

    chamadas = []

    @_repetir_se_a_conexao_cair
    def consultar():
        chamadas.append(1)
        if len(chamadas) < 3:
            raise httpx.RemoteProtocolError("Server disconnected")
        return "ok"

    assert consultar() == "ok"
    assert len(chamadas) == 3


def test_erro_inesperado_vira_mensagem_clara(falsos):
    from fastapi.testclient import TestClient

    from app.main import app

    falsos[0].listar_temas = lambda: 1 / 0
    resposta = TestClient(app, raise_server_exceptions=False).get("/api/temas")

    assert resposta.status_code == 500
    assert resposta.json()["detail"].startswith("Ocorreu um erro inesperado")
