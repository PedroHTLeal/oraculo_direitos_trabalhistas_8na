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
        resposta = self.respostas.pop(0)
        if isinstance(resposta, Exception):
            raise resposta
        return resposta


def test_responde_em_json_com_os_trechos():
    resultado = {"encontrou": True, "resposta": "30 dias.", "trechos_usados": [7]}
    cliente = ClienteFalso([resposta_falsa(json.dumps(resultado))])
    assistente = AssistenteIA(cliente=cliente, modelo="modelo-teste")

    assert assistente.responder("Quantos dias?", [{"id": 7, "tema": "Férias", "secao": "Geral", "texto": "30"}]) == resultado
    chamada = cliente.chamadas[0]
    assert chamada["model"] == "modelo-teste"
    assert '<trecho numero="7"' in chamada["contents"]
    assert chamada["config"].response_mime_type == "application/json"


def test_modelo_sobrecarregado_usa_o_modelo_reserva():
    from google.genai import errors

    resultado = {"encontrou": True, "resposta": "30 dias.", "trechos_usados": [7]}
    sobrecarga = errors.ServerError(503, {"error": {"code": 503, "message": "high demand", "status": "UNAVAILABLE"}})
    cliente = ClienteFalso([sobrecarga, resposta_falsa(json.dumps(resultado))])

    assert AssistenteIA(cliente=cliente, modelo="principal").responder("Quantos dias?", []) == resultado
    assert [c["model"] for c in cliente.chamadas] == ["principal", ia.MODELO_RESERVA]


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

