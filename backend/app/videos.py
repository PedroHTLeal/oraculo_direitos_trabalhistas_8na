"""Vídeos do YouTube sobre a pergunta, para o e-mail do "Saber mais".

Com a chave da API oficial do YouTube (YOUTUBE_API_KEY, gratuita), o sistema pesquisa os
vídeos mais relevantes para a pergunta e envia o link direto de cada um: o vídeo abre no
site ou no aplicativo do YouTube. Sem a chave, envia o link da pesquisa no YouTube, já
filtrada para mostrar só vídeos.
"""

import logging
import urllib.parse
from html import unescape

import httpx

logger = logging.getLogger("oraculo")

PESQUISA_API = "https://www.googleapis.com/youtube/v3/search"
# Filtro "Tipo: vídeo" da pesquisa do YouTube (tira canais, playlists e Shorts da lista)
FILTRO_SO_VIDEOS = "EgIQAQ%253D%253D"


def link_da_pesquisa(pergunta):
    return (
        "https://www.youtube.com/results?search_query="
        + urllib.parse.quote_plus(pergunta.strip())
        + "&sp="
        + FILTRO_SO_VIDEOS
    )


class BuscadorYouTube:
    """Pesquisa vídeos pela API oficial do YouTube (YouTube Data API v3)."""

    def __init__(self, chave, cliente=None):
        self.chave = chave
        self.cliente = cliente or httpx.Client(timeout=10)

    def buscar(self, pergunta, quantidade=2):
        resposta = self.cliente.get(
            PESQUISA_API,
            params={
                "part": "snippet",
                "q": pergunta,
                "type": "video",
                "maxResults": quantidade,
                "regionCode": "BR",
                "relevanceLanguage": "pt",
                "safeSearch": "strict",
                "key": self.chave,
            },
        )
        resposta.raise_for_status()
        videos = []
        for item in resposta.json().get("items", []):
            trecho = item["snippet"]
            videos.append(
                {
                    "titulo": f"{unescape(trecho['title'])} ({unescape(trecho['channelTitle'])})",
                    "url": f"https://www.youtube.com/watch?v={item['id']['videoId']}",
                }
            )
        return videos
