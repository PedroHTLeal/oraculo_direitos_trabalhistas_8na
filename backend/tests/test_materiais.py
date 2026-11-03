from app.materiais import CLT, escolher_assunto, montar_materiais, normalizar

CADASTRADOS = [
    {"assunto": "Férias", "palavras_chave": ["ferias"], "tipo": "video", "titulo": "V1", "url": "https://www.youtube.com/watch?v=1", "ordem": 1},
    {"assunto": "Férias", "palavras_chave": ["ferias"], "tipo": "video", "titulo": "V2", "url": "https://www.youtube.com/watch?v=2", "ordem": 2},
    {"assunto": "Férias", "palavras_chave": ["ferias"], "tipo": "site", "titulo": "S1", "url": "https://site.com.br/ferias", "ordem": 1},
    {"assunto": "13º salário", "palavras_chave": ["13", "decimo terceiro"], "tipo": "video", "titulo": "V13", "url": "https://www.youtube.com/watch?v=13", "ordem": 1},
]
CARTILHA = "https://www.trt4.jus.br/portais/trt4/ferias"


def test_normaliza_acentos_e_simbolos():
    assert normalizar("Quando o 13º Salário é pago?") == "quando o 13o salario e pago?"


def test_escolhe_o_assunto_pelas_palavras_da_pergunta():
    assert escolher_assunto("Quantos dias de FÉRIAS eu tenho?", CADASTRADOS) == "Férias"
    assert escolher_assunto("Quando o 13º salário deve ser pago?", CADASTRADOS) == "13º salário"
    assert escolher_assunto("Como recebo o décimo terceiro?", CADASTRADOS) == "13º salário"
    assert escolher_assunto("Quanto é a hora extra?", CADASTRADOS) is None
    # "13" só conta como palavra, não dentro de outro número
    assert escolher_assunto("Trabalho desde 2013", CADASTRADOS) is None


def test_assunto_cadastrado_usa_os_links_da_equipe_e_completa_com_a_cartilha():
    materiais = montar_materiais("Posso vender minhas férias?", "Férias", CARTILHA, CADASTRADOS)

    assert [s["url"] for s in materiais["sites"]] == ["https://site.com.br/ferias", CARTILHA]
    assert [v["url"] for v in materiais["videos"]] == ["https://www.youtube.com/watch?v=1", "https://www.youtube.com/watch?v=2"]


def test_assunto_sem_links_envia_cartilha_lei_e_busca_no_youtube():
    materiais = montar_materiais("Quanto é a hora extra?", "Jornada de Trabalho", "https://trt4/jornada", CADASTRADOS)

    assert [s["url"] for s in materiais["sites"]] == ["https://trt4/jornada", CLT[1]]
    assert materiais["videos"][0]["url"].startswith("https://www.youtube.com/results?search_query=Jornada")


def test_tema_com_lei_propria():
    materiais = montar_materiais("Estagiário tem recesso?", "Contrato de Estágio", None, [])

    assert "11.788" in materiais["sites"][0]["titulo"]
