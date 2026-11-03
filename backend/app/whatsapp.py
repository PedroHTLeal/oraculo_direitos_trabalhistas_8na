import httpx

LIMITE_MENSAGEM = 1500  # mantém as mensagens curtas e fáceis de ler no celular


class ErroEnvioWhatsApp(RuntimeError):
    pass


class EnviadorN8n:
    """Envia mensagens de WhatsApp por um fluxo do n8n (automacao/fluxo-oraculo-whatsapp.json).

    O Oráculo só avisa o n8n "envie este texto para este telefone"; o n8n confere
    como o número está registrado no WhatsApp (com ou sem o 9 extra) e envia pela
    Evolution API, ligada a um WhatsApp por QR code.
    """

    def __init__(self, url_webhook, token, cliente=None):
        self.url = url_webhook
        self.cabecalhos = {"X-Oraculo-Token": token}
        self.cliente = cliente or httpx.Client(timeout=60)

    def enviar(self, telefone, texto):
        corpo = {"telefone": telefone.lstrip("+"), "mensagem": texto}
        try:
            resposta = self.cliente.post(self.url, json=corpo, headers=self.cabecalhos)
        except httpx.HTTPError as erro:
            raise ErroEnvioWhatsApp(
                "Não foi possível falar com o n8n. Confira se a automação está ligada (automacao/iniciar-automacao.bat)."
            ) from erro
        if resposta.status_code == 404:
            raise ErroEnvioWhatsApp("O fluxo do n8n não está ativo. Ative o fluxo \"Oráculo - envio de WhatsApp\" no n8n.")
        if not resposta.is_success:
            raise ErroEnvioWhatsApp(f"O n8n não conseguiu enviar (erro {resposta.status_code}): {_detalhe(resposta)}")


def _detalhe(resposta):
    try:
        dados = resposta.json()
    except ValueError:
        return resposta.text[:200]
    return dados.get("message") or dados.get("erro") or str(dados)[:200]


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
