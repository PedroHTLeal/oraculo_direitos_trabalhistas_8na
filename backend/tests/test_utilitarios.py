import pytest

from app.ia import eh_video_youtube, filtrar_materiais, formatar_trechos
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


def test_filtra_links_que_nao_vieram_da_pesquisa():
    sugeridos = {
        "sites": [
            {"titulo": "Inventado", "url": "https://site-inventado.com"},
            {"titulo": "Gov", "url": "https://www.gov.br/a"},
            {"titulo": "Vídeo no lugar errado", "url": "https://www.youtube.com/watch?v=x"},
            {"titulo": "TST", "url": "https://www.tst.jus.br/b"},
            {"titulo": "Terceiro", "url": "https://www.mpt.mp.br/c"},
        ],
        "videos": [
            {"titulo": "Canal", "url": "https://www.youtube.com/@canal"},
            {"titulo": "V1", "url": "https://www.youtube.com/watch?v=1"},
            {"titulo": "V1 repetido", "url": "https://www.youtube.com/watch?v=1"},
            {"titulo": "V2", "url": "https://youtu.be/2"},
        ],
    }
    pesquisadas = {
        "https://www.gov.br/a",
        "https://www.youtube.com/watch?v=x",
        "https://www.tst.jus.br/b",
        "https://www.mpt.mp.br/c",
        "https://www.youtube.com/@canal",
        "https://www.youtube.com/watch?v=1",
        "https://youtu.be/2",
    }

    materiais = filtrar_materiais(sugeridos, pesquisadas)

    assert [s["url"] for s in materiais["sites"]] == ["https://www.gov.br/a", "https://www.tst.jus.br/b"]
    assert [v["url"] for v in materiais["videos"]] == ["https://www.youtube.com/watch?v=1", "https://youtu.be/2"]


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
