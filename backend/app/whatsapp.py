from twilio.rest import Client

LIMITE_MENSAGEM = 1500  # o WhatsApp via Twilio aceita até 1600 caracteres


class EnviadorWhatsApp:
    """Envia mensagens de WhatsApp pelo Sandbox da Twilio."""

    def __init__(self, account_sid, auth_token, numero_remetente):
        self.cliente = Client(account_sid, auth_token)
        self.remetente = f"whatsapp:{numero_remetente}"

    def enviar(self, telefone, texto):
        self.cliente.messages.create(from_=self.remetente, to=f"whatsapp:{telefone}", body=texto)


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
