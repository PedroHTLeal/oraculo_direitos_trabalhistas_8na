import pytest

from app.ia import eh_video_youtube, formatar_trechos, resolver_link, separar_materiais
from app.repositorio import diversificar


@pytest.mark.parametrize(
    "url, esperado",
    [
        ("https://www.youtube.com/watch?v=abc123", True),
        ("https://youtu.be/abc123", True),
        ("https://m.youtube.com/watch?v=abc123", True),
        ("https://www.youtube.com/@canal", False),
        ("https://www.youtube.com/results?search_query=ferias", False),
        ("https://www.gov.br/trabalho", False),
    ],
)
def test_identifica_videos_do_youtube(url, esperado):
    assert eh_video_youtube(url) is esperado


def test_separa_sites_e_videos_sem_repeticoes():
    links = [
        {"titulo": "Gov", "url": "https://www.gov.br/a"},
        {"titulo": "Canal", "url": "https://www.youtube.com/@canal"},
        {"titulo": "V1", "url": "https://www.youtube.com/watch?v=1"},
        {"titulo": "Gov repetido", "url": "https://www.gov.br/a"},
        {"titulo": "TST", "url": "https://www.tst.jus.br/b"},
        {"titulo": "V1 repetido", "url": "https://www.youtube.com/watch?v=1"},
        {"titulo": "V2", "url": "https://youtu.be/2"},
        {"titulo": "MPT", "url": "https://www.mpt.mp.br/c"},
        {"titulo": "V3", "url": "https://youtu.be/3"},
    ]

    materiais = separar_materiais(links)

    assert [s["url"] for s in materiais["sites"]] == ["https://www.gov.br/a", "https://www.tst.jus.br/b"]
    assert [v["url"] for v in materiais["videos"]] == ["https://www.youtube.com/watch?v=1", "https://youtu.be/2"]


def test_links_comuns_nao_passam_pelo_redirecionamento():
    assert resolver_link("https://www.gov.br/a") == "https://www.gov.br/a"


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
