import pytest

from app.ia import eh_video_youtube, formatar_trechos, resolver_link, separar_materiais
from app.repositorio import diversificar
from app.telefone import TelefoneInvalido, normalizar_telefone
from app.whatsapp import LIMITE_MENSAGEM, montar_mensagem


@pytest.mark.parametrize(
    "entrada",
    ["(51) 99999-8888", "51999998888", "+55 51 99999-8888", "5551999998888"],
)
def test_normaliza_telefones_validos(entrada):
    assert normalizar_telefone(entrada) == "+5551999998888"


def test_aceita_telefone_fixo_com_8_digitos():
    assert normalizar_telefone("(11) 3333-4444") == "+551133334444"


@pytest.mark.parametrize("entrada", ["", "12345", "(05) 99999-8888", "(51) 09999-8888", "519999988881234"])
def test_rejeita_telefones_invalidos(entrada):
    with pytest.raises(TelefoneInvalido):
        normalizar_telefone(entrada)


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


def test_mensagem_longa_e_encurtada_sem_perder_links():
    materiais = {
        "sites": [{"titulo": "Gov", "url": "https://www.gov.br/a"}],
        "videos": [{"titulo": "Vídeo", "url": "https://youtu.be/2"}],
    }
    mensagem = montar_mensagem("Pergunta?", "palavra " * 500, materiais)

    assert len(mensagem) <= LIMITE_MENSAGEM
    assert "https://www.gov.br/a" in mensagem
    assert "https://youtu.be/2" in mensagem


def test_diversifica_trechos_por_tema():
    trechos = [{"id": i, "tema": "Férias"} for i in range(5)] + [
        {"id": 10, "tema": "Contrato de Estágio"},
        {"id": 11, "tema": "Rescisão"},
    ]
    escolhidos = diversificar(trechos, limite=6)

    assert [t["id"] for t in escolhidos] == [0, 1, 2, 10, 11]
