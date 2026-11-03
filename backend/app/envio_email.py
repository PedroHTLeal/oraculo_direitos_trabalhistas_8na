"""Envio de e-mails pelo Gmail (SMTP), com uma senha de app do remetente."""

import smtplib
from email.message import EmailMessage
from email.utils import formataddr
from html import escape

AVISO = "Conteúdo informativo. Em caso de dúvida, procure um advogado, o sindicato ou a Justiça do Trabalho."


class ErroEnvioEmail(RuntimeError):
    pass


class EnviadorEmail:
    def __init__(self, remetente, senha, servidor="smtp.gmail.com", porta=587, conectar=smtplib.SMTP):
        self.remetente = remetente
        self.senha = senha
        self.servidor = servidor
        self.porta = porta
        self.conectar = conectar

    def enviar(self, destinatario, conteudo):
        mensagem = EmailMessage()
        mensagem["Subject"] = conteudo["assunto"]
        mensagem["From"] = formataddr(("Oráculo dos Direitos Trabalhistas", self.remetente))
        mensagem["To"] = destinatario
        mensagem.set_content(conteudo["texto"])
        mensagem.add_alternative(conteudo["html"], subtype="html")
        try:
            with self.conectar(self.servidor, self.porta, timeout=30) as smtp:
                smtp.starttls()
                smtp.login(self.remetente, self.senha)
                smtp.send_message(mensagem)
        except smtplib.SMTPAuthenticationError as erro:
            raise ErroEnvioEmail(
                "O Gmail recusou o login. Confira EMAIL_REMETENTE e EMAIL_SENHA_APP (senha de app) no backend/.env."
            ) from erro
        except smtplib.SMTPRecipientsRefused as erro:
            raise ErroEnvioEmail("O endereço de e-mail foi recusado pelo servidor.") from erro
        except (smtplib.SMTPException, OSError) as erro:
            raise ErroEnvioEmail(f"Não foi possível enviar o e-mail: {erro}") from erro


def _paragrafos(texto):
    return "".join(f"<p>{escape(p).replace(chr(10), '<br>')}</p>" for p in texto.split("\n\n") if p.strip())


def _lista_html(titulo, itens):
    if not itens:
        return ""
    links = "".join(f'<li><a href="{escape(i["url"])}">{escape(i["titulo"])}</a></li>' for i in itens)
    return f"<h3>{titulo}</h3><ul>{links}</ul>"


def _lista_texto(titulo, itens):
    if not itens:
        return []
    return ["", titulo] + [f"- {i['titulo']}\n  {i['url']}" for i in itens]


def _html(titulo, corpo):
    return (
        '<div style="font-family:Arial,sans-serif;max-width:600px;margin:auto;color:#030C2C">'
        f'<div style="background:#030C2C;color:#E8B20F;padding:16px 20px;font-size:18px"><b>{titulo}</b></div>'
        f'<div style="padding:8px 20px;line-height:1.5">{corpo}'
        f'<p style="color:#666;font-size:12px;margin-top:24px">{AVISO}</p></div></div>'
    )


def montar_email_conteudo(nome, pergunta, resposta, materiais):
    """Resposta da cartilha com 2 sites e 2 vídeos sobre o assunto."""
    texto = [
        f"Olá, {nome}!",
        "",
        f"Você perguntou: {pergunta}",
        "",
        resposta,
        *_lista_texto("Para ler mais:", materiais["sites"]),
        *_lista_texto("Vídeos sobre o assunto:", materiais["videos"]),
        "",
        AVISO,
    ]
    corpo = (
        f"<p>Olá, {escape(nome)}!</p>"
        f"<p><b>Você perguntou:</b> <i>{escape(pergunta)}</i></p>"
        f"{_paragrafos(resposta)}"
        f'{_lista_html("Para ler mais", materiais["sites"])}'
        f'{_lista_html("Vídeos sobre o assunto", materiais["videos"])}'
    )
    return {
        "assunto": "Oráculo: mais sobre a sua pergunta",
        "texto": "\n".join(texto),
        "html": _html("Oráculo dos Direitos Trabalhistas", corpo),
    }


def montar_email_atualizacao(tema, titulo, conteudo, url):
    """Novidade sobre um tema que a pessoa acompanha."""
    texto = [titulo, "", conteudo]
    corpo = f"<h2>{escape(titulo)}</h2>{_paragrafos(conteudo)}"
    if url:
        texto += ["", f"Saiba mais: {url}"]
        corpo += f'<p><a href="{escape(url)}">Saiba mais</a></p>'
    rodape = "Você recebe este e-mail porque acompanha este tema no Oráculo."
    texto += ["", rodape]
    corpo += f"<p>{rodape}</p>"
    return {
        "assunto": f"Oráculo: novidade sobre {tema}",
        "texto": "\n".join(texto),
        "html": _html(f"Novidade sobre {escape(tema)}", corpo),
    }
