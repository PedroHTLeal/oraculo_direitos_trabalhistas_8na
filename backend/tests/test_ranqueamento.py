from app.ranqueamento import Corpus, expandir, raizes, reordenar

CARTILHA = [
    {"tema": "Rescisão", "secao": "Data de saída na Carteira de Trabalho", "texto": "A carteira assinada deve ter a data de saída."},
    {"tema": "Jornada", "secao": "Jornada 12x36", "texto": "O acordo assinado com a carteira de trabalho vale."},
    {"tema": "Seguro", "secao": "Quem tem direito", "texto": "Precisa ter a carteira assinada por 12 meses."},
    {"tema": "Salário", "secao": "Tipos de salário", "texto": "Quem trabalha 1 ou 2 dias é diarista; com mais dias, carteira assinada."},
]


def test_raizes_ignoram_acentos_plural_e_palavras_vazias():
    assert raizes("Diaristas têm carteira assinada?") == {"diari", "carte", "assin"}


def test_palavra_rara_pesa_mais_que_palavra_comum():
    corpus = Corpus(CARTILHA)
    assert corpus.peso("diari") > corpus.peso("carte")


def test_trecho_com_a_palavra_rara_sobe_para_o_topo():
    # Na ordem do banco, o trecho sobre diaristas vinha por último
    candidatos = [dict(t, relevancia=4 - i) for i, t in enumerate(CARTILHA)]

    ordenados = reordenar("Diarista tem carteira assinada?", candidatos, Corpus(CARTILHA))

    assert ordenados[0]["secao"] == "Tipos de salário"


def test_sinonimos_entram_na_pergunta():
    sinonimos = [{"termo": "patrao", "equivalentes": "empregador"}]
    assert "empregador" in expandir("Meu patrão não paga", sinonimos)
    assert expandir("Meu trabalho", sinonimos) == "Meu trabalho"


def test_empate_mantem_a_ordem_do_banco():
    candidatos = [{"tema": "A", "secao": "x", "texto": "nada", "relevancia": 1}, {"tema": "B", "secao": "y", "texto": "nada", "relevancia": 2}]
    assert [c["tema"] for c in reordenar("ferias", candidatos, Corpus(candidatos))] == ["B", "A"]
