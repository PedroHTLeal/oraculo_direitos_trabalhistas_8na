import httpx

from app.materiais import montar_materiais
from app.videos import BuscadorYouTube

RESPOSTA_API = {
    "items": [
        {"id": {"videoId": "abc123"}, "snippet": {"title": "Atestado e INSS: os 15 dias", "channelTitle": "Canal &amp; Direito"}},
        {"id": {"videoId": "def456"}, "snippet": {"title": "Afastamento pelo INSS", "channelTitle": "TRT"}},
    ]
}


def cliente_falso(pedidos, status=200):
    def responder(pedido):
        pedidos.append(pedido)
        return httpx.Response(status, json=RESPOSTA_API)

    return httpx.Client(transport=httpx.MockTransport(responder))


def test_busca_os_videos_mais_relevantes_para_a_pergunta():
    pedidos = []
    videos = BuscadorYouTube("chave-teste", cliente_falso(pedidos)).buscar("Atestado e INSS?", 2)

    assert videos == [
        {"titulo": "Atestado e INSS: os 15 dias (Canal & Direito)", "url": "https://www.youtube.com/watch?v=abc123"},
        {"titulo": "Afastamento pelo INSS (TRT)", "url": "https://www.youtube.com/watch?v=def456"},
    ]
    parametros = pedidos[0].url.params
    assert parametros["q"] == "Atestado e INSS?"
    assert parametros["type"] == "video"
    assert parametros["regionCode"] == "BR"
    assert parametros["relevanceLanguage"] == "pt"


def test_email_traz_os_videos_da_api_quando_nao_ha_videos_da_equipe():
    buscador = BuscadorYouTube("chave", cliente_falso([]))

    materiais = montar_materiais("Atestado e INSS?", "Suspensão", None, [], buscador)

    assert [v["url"] for v in materiais["videos"]] == ["https://www.youtube.com/watch?v=abc123", "https://www.youtube.com/watch?v=def456"]


def test_falha_da_api_volta_para_a_pesquisa_no_youtube():
    buscador = BuscadorYouTube("chave", cliente_falso([], status=403))

    materiais = montar_materiais("Atestado e INSS?", "Suspensão", None, [], buscador)

    assert materiais["videos"][0]["url"].startswith("https://www.youtube.com/results?search_query=Atestado")


def test_videos_escolhidos_pela_equipe_tem_prioridade():
    pedidos = []
    cadastrados = [{"assunto": "INSS", "palavras_chave": ["inss"], "tipo": "video", "titulo": "V", "url": "https://www.youtube.com/watch?v=equipe", "ordem": 1}]

    materiais = montar_materiais("Atestado e INSS?", "Suspensão", None, cadastrados, BuscadorYouTube("chave", cliente_falso(pedidos)))

    assert materiais["videos"][0]["url"] == "https://www.youtube.com/watch?v=equipe"
    assert pedidos == []
