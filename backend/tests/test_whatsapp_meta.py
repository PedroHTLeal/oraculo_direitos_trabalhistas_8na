import json

import httpx
import pytest

from app.config import Configuracao
from app.dependencias import obter_configuracao, obter_whatsapp
from app.main import app
from app.whatsapp import EnviadorMetaCloud, EnviadorTwilio, ErroEnvioWhatsApp, sem_nono_digito


def enviador_com(respostas):
    """Cria o enviador da Meta com respostas simuladas e guarda os pedidos feitos."""
    pedidos = []

    def responder(pedido):
        pedidos.append(json.loads(pedido.content))
        status, corpo = respostas.pop(0)
        return httpx.Response(status, json=corpo)

    cliente = httpx.Client(transport=httpx.MockTransport(responder))
    return EnviadorMetaCloud("token-teste", "123456", cliente=cliente), pedidos


def erro(codigo, mensagem="falhou"):
    return 400, {"error": {"code": codigo, "message": mensagem}}


SUCESSO = (200, {"messages": [{"id": "wamid.1"}]})


def test_envia_texto_pela_api_oficial():
    enviador, pedidos = enviador_com([SUCESSO])

    enviador.enviar("+5551999998888", "Olá")

    assert pedidos == [
        {"messaging_product": "whatsapp", "to": "5551999998888", "type": "text", "text": {"body": "Olá", "preview_url": True}}
    ]
    assert enviador.url == "https://graph.facebook.com/v23.0/123456/messages"


def test_tenta_de_novo_sem_o_nono_digito():
    # Número de teste da Meta: o celular pode estar cadastrado sem o 9 extra
    enviador, pedidos = enviador_com([erro(131030), SUCESSO])

    enviador.enviar("+5551999998888", "Olá")

    assert [p["to"] for p in pedidos] == ["5551999998888", "555199998888"]


@pytest.mark.parametrize(
    "codigo, trecho",
    [
        (190, "token de acesso da Meta expirou"),
        (131047, "24 horas"),
        (131030, "lista de números de teste"),
        (100, "falhou"),
    ],
)
def test_erros_da_meta_viram_mensagens_claras(codigo, trecho):
    enviador, _ = enviador_com([erro(codigo), erro(codigo)])

    with pytest.raises(ErroEnvioWhatsApp, match=trecho):
        enviador.enviar("+5511900000001", "Olá")


@pytest.mark.parametrize(
    "numero, esperado",
    [("5551999998888", "555199998888"), ("551133334444", None), ("14155238886", None)],
)
def test_remove_o_nono_digito_so_de_celular_brasileiro(numero, esperado):
    assert sem_nono_digito(numero) == esperado


def configuracao(**campos):
    base = dict(
        supabase_url="https://x.supabase.co",
        supabase_chave_servico="chave",
        twilio_account_sid="AC1",
        twilio_auth_token="token",
        twilio_whatsapp_numero="+14155238886",
        twilio_sandbox_codigo="join teste",
    )
    return Configuracao(**{**base, **campos})


def test_escolhe_o_servico_pelo_env(monkeypatch):
    import app.dependencias as dependencias

    obter_whatsapp.cache_clear()
    monkeypatch.setattr(dependencias, "obter_configuracao", lambda: configuracao())
    assert isinstance(obter_whatsapp(), EnviadorTwilio)

    obter_whatsapp.cache_clear()
    monkeypatch.setattr(
        dependencias,
        "obter_configuracao",
        lambda: configuracao(provedor_whatsapp="meta", meta_token="t", meta_phone_number_id="99"),
    )
    assert isinstance(obter_whatsapp(), EnviadorMetaCloud)
    obter_whatsapp.cache_clear()


def test_instrucoes_para_o_numero_da_meta(client, falsos):
    app.dependency_overrides[obter_configuracao] = lambda: configuracao(
        provedor_whatsapp="meta", meta_token="t", meta_phone_number_id="99", meta_numero="+1 555 012 3456"
    )

    assert client.get("/api/whatsapp").json() == {"numero": "+1 555 012 3456", "codigo": "Oi"}
