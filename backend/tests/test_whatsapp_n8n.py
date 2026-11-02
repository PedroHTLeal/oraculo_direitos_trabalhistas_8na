import json
from pathlib import Path

import httpx
import pytest

from app.config import Configuracao
from app.whatsapp import EnviadorN8n, ErroEnvioWhatsApp

URL = "http://localhost:5678/webhook/oraculo-whatsapp"
FLUXO = Path(__file__).resolve().parents[2] / "automacao" / "fluxo-oraculo-whatsapp.json"


def enviador_com(resposta=None, falha=None):
    """Enviador do n8n com resposta simulada; guarda os pedidos feitos."""
    pedidos = []

    def responder(pedido):
        pedidos.append(pedido)
        if falha:
            raise falha
        return resposta

    cliente = httpx.Client(transport=httpx.MockTransport(responder))
    return EnviadorN8n(URL, "token-teste", cliente=cliente), pedidos


def test_envia_telefone_e_mensagem_ao_n8n():
    enviador, pedidos = enviador_com(httpx.Response(200, json={"id": "true_5581@c.us_ABC"}))

    enviador.enviar("+5581983409271", "Olá")

    assert str(pedidos[0].url) == URL
    assert pedidos[0].headers["X-Oraculo-Token"] == "token-teste"
    assert json.loads(pedidos[0].content) == {"telefone": "5581983409271", "mensagem": "Olá"}


@pytest.mark.parametrize(
    "resposta, falha, trecho",
    [
        (None, httpx.ConnectError("recusado"), "automação está ligada"),
        (httpx.Response(404, json={"message": "not registered"}), None, "não está ativo"),
        (httpx.Response(500, json={"message": "Este número não tem WhatsApp."}), None, "não tem WhatsApp"),
    ],
)
def test_falhas_viram_mensagens_claras(resposta, falha, trecho):
    enviador, _ = enviador_com(resposta, falha)

    with pytest.raises(ErroEnvioWhatsApp, match=trecho):
        enviador.enviar("+5581983409271", "Olá")


def test_sem_n8n_configurado_o_envio_fica_indisponivel(monkeypatch):
    import app.dependencias as dependencias
    from app.config import ConfiguracaoAusente

    dependencias.obter_whatsapp.cache_clear()
    monkeypatch.setattr(dependencias, "obter_configuracao", lambda: Configuracao("https://x.supabase.co", "chave"))
    with pytest.raises(ConfiguracaoAusente):
        dependencias.obter_whatsapp()
    dependencias.obter_whatsapp.cache_clear()


def test_fluxo_do_n8n_esta_completo():
    # O arquivo importado no n8n precisa ligar todas as etapas, na ordem
    fluxo = json.loads(FLUXO.read_text(encoding="utf-8"))
    nomes = [no["name"] for no in fluxo["nodes"]]
    assert nomes == [
        "Pedido do Oráculo",
        "Validar pedido",
        "Conferir número no WhatsApp",
        "Número tem WhatsApp?",
        "Enviar mensagem",
    ]
    for origem, destino in zip(nomes, nomes[1:]):
        assert fluxo["connections"][origem]["main"][0][0]["node"] == destino
    assert fluxo["nodes"][0]["parameters"]["path"] == "oraculo-whatsapp"
