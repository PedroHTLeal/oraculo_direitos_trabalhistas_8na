import httpx
from twilio.rest import Client

LIMITE_MENSAGEM = 1500  # a Twilio aceita até 1600 caracteres e a Meta até 4096; vale o menor

# Erros da WhatsApp Cloud API (Meta) traduzidos para quem acompanha o envio
ERROS_META = {
    190: "O token de acesso da Meta expirou ou é inválido. Gere um novo e atualize o backend/.env.",
    131030: "Este número não está na lista de números de teste do WhatsApp Cloud API (painel da Meta).",
    131047: "A pessoa precisa enviar uma mensagem para o número do Oráculo antes (o WhatsApp só permite "
    "respostas livres até 24 horas depois da última mensagem dela).",
}


class ErroEnvioWhatsApp(RuntimeError):
    pass


class EnviadorTwilio:
    """Envia mensagens de WhatsApp pelo Sandbox da Twilio."""

    def __init__(self, account_sid, auth_token, numero_remetente):
        self.cliente = Client(account_sid, auth_token)
        self.remetente = f"whatsapp:{numero_remetente}"

    def enviar(self, telefone, texto):
        self.cliente.messages.create(from_=self.remetente, to=f"whatsapp:{telefone}", body=texto)


def sem_nono_digito(numero):
    """55 + DDD + 9XXXXXXXX -> 55 + DDD + XXXXXXXX.

    O WhatsApp identifica muitos celulares brasileiros antigos sem o 9 extra;
    o número de teste da Meta só aceita destinatários exatamente como cadastrados.
    """
    if numero.startswith("55") and len(numero) == 13 and numero[4] == "9":
        return numero[:4] + numero[5:]
    return None


class EnviadorMetaCloud:
    """Envia mensagens pela WhatsApp Cloud API, a API oficial da Meta."""

    def __init__(self, token, phone_number_id, versao_api="v23.0", cliente=None):
        self.url = f"https://graph.facebook.com/{versao_api}/{phone_number_id}/messages"
        self.cliente = cliente or httpx.Client(timeout=20)
        self.cabecalhos = {"Authorization": f"Bearer {token}"}

    def _postar(self, numero, texto):
        corpo = {
            "messaging_product": "whatsapp",
            "to": numero,
            "type": "text",
            "text": {"body": texto, "preview_url": True},
        }
        return self.cliente.post(self.url, json=corpo, headers=self.cabecalhos)

    def enviar(self, telefone, texto):
        numero = telefone.lstrip("+")
        resposta = self._postar(numero, texto)
        codigo = _codigo_erro(resposta)
        alternativo = sem_nono_digito(numero)
        if codigo == 131030 and alternativo:
            resposta = self._postar(alternativo, texto)
            codigo = _codigo_erro(resposta)
        if resposta.is_success:
            return
        detalhe = ERROS_META.get(codigo) or _mensagem_erro(resposta)
        raise ErroEnvioWhatsApp(f"WhatsApp Cloud API (erro {codigo or resposta.status_code}): {detalhe}")


def _corpo(resposta):
    try:
        return resposta.json()
    except ValueError:
        return {}


def _codigo_erro(resposta):
    if resposta.is_success:
        return None
    return (_corpo(resposta).get("error") or {}).get("code")


def _mensagem_erro(resposta):
    return (_corpo(resposta).get("error") or {}).get("message") or resposta.text[:200]


def _juntar(pergunta, resposta, materiais):
    linhas = [
        "*Oráculo dos Direitos Trabalhistas*",
        "",
        f"Você perguntou: _{pergunta}_",
        "",
        resposta,
    ]
    if materiais["sites"]:
        linhas += ["", "*Para ler mais:*"]
        linhas += [f"• {item['titulo']}\n{item['url']}" for item in materiais["sites"]]
    if materiais["videos"]:
        linhas += ["", "*Vídeos sobre o assunto:*"]
        linhas += [f"• {item['titulo']}\n{item['url']}" for item in materiais["videos"]]
    linhas += ["", "Conteúdo informativo. Em caso de dúvida, procure um advogado, o sindicato ou a Justiça do Trabalho."]
    return "\n".join(linhas)


def montar_mensagem(pergunta, resposta, materiais):
    # Encurta a resposta, se preciso, para a mensagem caber no limite sem perder os links
    espaco = LIMITE_MENSAGEM - len(_juntar(pergunta, "", materiais))
    if len(resposta) > espaco:
        resposta = resposta[: max(espaco - 3, 0)].rstrip() + "..."
    return _juntar(pergunta, resposta, materiais)


def montar_mensagem_atualizacao(tema, titulo, conteudo, url):
    linhas = [f"*Oráculo · Novidade sobre {tema}*", "", f"*{titulo}*", "", conteudo]
    if url:
        linhas += ["", f"Saiba mais: {url}"]
    linhas += ["", "Você recebe esta mensagem porque acompanha este tema no Oráculo."]
    return "\n".join(linhas)[:LIMITE_MENSAGEM]
