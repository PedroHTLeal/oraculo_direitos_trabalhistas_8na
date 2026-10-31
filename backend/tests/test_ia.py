import json
from types import SimpleNamespace

import pytest
from google.genai import types

from app import ia
from app.ia import AssistenteIA, RecusaDaIA


def resposta_falsa(texto="", fontes=(), finish_reason=types.FinishReason.STOP, bloqueada=False):
    chunks = [SimpleNamespace(web=SimpleNamespace(uri=uri, title=titulo, domain=None)) for uri, titulo in fontes]
    candidato = SimpleNamespace(
        finish_reason=finish_reason,
        grounding_metadata=SimpleNamespace(grounding_chunks=chunks),
    )
    return SimpleNamespace(
        text=texto,
        candidates=[candidato],
        prompt_feedback=SimpleNamespace(block_reason="SAFETY") if bloqueada else None,
    )


class ClienteFalso:
    def __init__(self, respostas):
        self.respostas = list(respostas)
        self.chamadas = []
        self.models = self

    def generate_content(self, model, contents, config):
        self.chamadas.append({"model": model, "contents": contents, "config": config})
        return self.respostas.pop(0)


def test_responde_em_json_com_os_trechos():
    resultado = {"encontrou": True, "resposta": "30 dias.", "trechos_usados": [7]}
    cliente = ClienteFalso([resposta_falsa(json.dumps(resultado))])
    assistente = AssistenteIA(cliente=cliente, modelo="modelo-teste")

    assert assistente.responder("Quantos dias?", [{"id": 7, "tema": "Férias", "secao": "Geral", "texto": "30"}]) == resultado
    chamada = cliente.chamadas[0]
    assert chamada["model"] == "modelo-teste"
    assert '<trecho numero="7"' in chamada["contents"]
    assert chamada["config"].response_mime_type == "application/json"


@pytest.mark.parametrize(
    "resposta",
    [
        resposta_falsa(finish_reason=types.FinishReason.SAFETY),
        resposta_falsa(bloqueada=True),
    ],
)
def test_resposta_bloqueada_vira_recusa(resposta):
    assistente = AssistenteIA(cliente=ClienteFalso([resposta]), modelo="m")
    with pytest.raises(RecusaDaIA):
        assistente.responder("pergunta", [])


def test_materiais_vem_das_fontes_da_pesquisa(monkeypatch):
    monkeypatch.setattr(ia, "buscar_titulo", lambda url, reserva: f"Título de {url}")
    sites = resposta_falsa("resumo", [("https://www.gov.br/ferias", "gov.br"), ("https://www.tst.jus.br/f", "tst.jus.br")])
    videos = resposta_falsa(
        "resumo",
        [("https://www.youtube.com/watch?v=a", "youtube.com"), ("https://youtu.be/b", "youtube.com")],
    )
    cliente = ClienteFalso([sites, videos])

    materiais = AssistenteIA(cliente=cliente, modelo="m").buscar_materiais("Quantos dias?", "Férias")

    assert [s["url"] for s in materiais["sites"]] == ["https://www.gov.br/ferias", "https://www.tst.jus.br/f"]
    assert [v["url"] for v in materiais["videos"]] == ["https://www.youtube.com/watch?v=a", "https://youtu.be/b"]
    assert materiais["sites"][0]["titulo"] == "Título de https://www.gov.br/ferias"
    assert all(chamada["config"].tools for chamada in cliente.chamadas)


def test_sem_videos_na_pesquisa_indica_busca_no_youtube(monkeypatch):
    monkeypatch.setattr(ia, "buscar_titulo", lambda url, reserva: reserva)
    cliente = ClienteFalso([resposta_falsa("r", [("https://www.gov.br/x", "gov.br")]), resposta_falsa("r")])

    materiais = AssistenteIA(cliente=cliente, modelo="m").buscar_materiais("Pergunta", "Férias")

    assert materiais["videos"][0]["url"] == "https://www.youtube.com/results?search_query=F%C3%A9rias"
