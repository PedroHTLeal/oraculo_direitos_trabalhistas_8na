"""Envio de e-mails pelo Gmail (SMTP), com uma senha de app do remetente."""

import smtplib
import urllib.parse
from email.message import EmailMessage
from email.utils import formataddr
from html import escape
from pathlib import Path

AVISO = "Conteúdo informativo. Em caso de dúvida, procure um advogado, o sindicato ou a Justiça do Trabalho."

# Imagens da identidade visual, anexadas ao e-mail (o Gmail não exibe SVG nem imagens de localhost).
# Geradas por scripts/gerar_imagens_email.py
RECURSOS = Path(__file__).resolve().parent / "recursos"
IMAGENS = {"simbolo@oraculo": "email-simbolo.png", "balanca@oraculo": "email-balanca.png"}

# Cores e fonte do site (frontend/src/index.css)
MARINHO = "#030C2C"
DOURADO = "#E8B20F"
DOURADO_ESCURO = "#A87A08"  # dourado legível sobre fundo branco
FUNDO_SUAVE = "#F1F2F6"
TEXTO = "#1C1C1C"
TEXTO_SUAVE = "#5C5C5C"
BORDA = "#E2E2E2"
FONTE = "'Plus Jakarta Sans','Segoe UI',Roboto,Helvetica,Arial,sans-serif"


class ErroEnvioEmail(RuntimeError):
    pass


class EnviadorEmail:
    def __init__(self, remetente, senha, servidor="smtp.gmail.com", porta=587, conectar=None):
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
        parte_html = mensagem.get_payload()[1]
        for cid, arquivo in IMAGENS.items():
            if f"cid:{cid}" in conteudo["html"]:
                parte_html.add_related((RECURSOS / arquivo).read_bytes(), "image", "png", cid=f"<{cid}>")
        try:
            conectar = self.conectar or smtplib.SMTP
            with conectar(self.servidor, self.porta, timeout=30) as smtp:
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
    estilo = f"margin:0 0 14px;font-size:16px;line-height:1.6;color:{TEXTO}"
    return "".join(
        f'<p style="{estilo}">{escape(p.strip()).replace(chr(10), "<br>")}</p>' for p in texto.split("\n\n") if p.strip()
    )


def _dominio(url):
    return urllib.parse.urlparse(url).netloc.lower().removeprefix("www.")


def _rotulo(texto):
    return (
        '<p style="margin:0 0 12px;font-size:11px;font-weight:700;letter-spacing:1.5px;'
        f'text-transform:uppercase;color:{DOURADO_ESCURO}">{texto}</p>'
    )


def _cartao(item, icone, fundo_icone, cor_icone):
    """Um link em forma de cartão: ícone à esquerda, título e endereço à direita."""
    url = escape(item["url"])
    return f"""
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin:0 0 10px;border:1px solid {BORDA};border-radius:12px">
  <tr>
    <td width="40" valign="middle" style="padding:14px 0 14px 14px">
      <a href="{url}" style="display:block;width:40px;height:40px;line-height:40px;border-radius:10px;background:{fundo_icone};color:{cor_icone};font-size:16px;font-weight:700;text-align:center;text-decoration:none">{icone}</a>
    </td>
    <td valign="middle" style="padding:14px">
      <a href="{url}" style="font-size:15px;font-weight:700;line-height:1.35;color:{MARINHO};text-decoration:none">{escape(item["titulo"])}</a>
      <div style="margin-top:3px;font-size:13px;color:{TEXTO_SUAVE}">{escape(_dominio(item["url"]))}</div>
    </td>
  </tr>
</table>"""


def _secao_links(titulo, itens, icone, fundo_icone, cor_icone):
    if not itens:
        return ""
    cartoes = "".join(_cartao(i, icone, fundo_icone, cor_icone) for i in itens)
    return f'<tr><td style="padding:8px 32px 18px">{_rotulo(titulo)}{cartoes}</td></tr>'


def _html(previa, chamada, titulo, corpo, rodape_extra=""):
    """Moldura do e-mail: cabeçalho e destaque em azul-escuro com o logo e a balança, como no site."""
    return f"""<!doctype html>
<html lang="pt-BR">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Oráculo dos Direitos Trabalhistas</title></head>
<body style="margin:0;padding:0;background:{FUNDO_SUAVE}">
<div style="display:none;max-height:0;overflow:hidden;opacity:0">{escape(previa)}</div>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:{FUNDO_SUAVE}">
<tr><td align="center" style="padding:24px 12px">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:600px;background:#FFFFFF;border-radius:16px;overflow:hidden;font-family:{FONTE}">

  <tr><td style="background:{MARINHO};padding:22px 32px 0">
    <table role="presentation" cellpadding="0" cellspacing="0"><tr>
      <td valign="middle"><img src="cid:simbolo@oraculo" width="32" height="32" alt="" style="display:block;border:0"></td>
      <td valign="middle" style="padding-left:10px;font-size:22px;font-weight:800;letter-spacing:-0.5px;color:#FFFFFF">Oráculo</td>
      <td valign="middle" style="padding:0 10px"><div style="width:1px;height:26px;background:#3A4363"></div></td>
      <td valign="middle" style="font-size:9px;font-weight:700;letter-spacing:1.4px;line-height:1.3;text-transform:uppercase;color:#B8BED3">Direitos<br>Trabalhistas</td>
    </tr></table>
  </td></tr>

  <tr><td style="background:{MARINHO};padding:28px 32px 32px">
    <table role="presentation" cellpadding="0" cellspacing="0"><tr>
      <td valign="middle"><img src="cid:balanca@oraculo" width="44" height="44" alt="" style="display:block;border:0"></td>
      <td valign="middle" style="padding-left:12px;font-size:11px;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;color:{DOURADO}">{chamada}</td>
    </tr></table>
    <h1 style="margin:18px 0 0;font-size:24px;line-height:1.3;font-weight:800;letter-spacing:-0.5px;color:#FFFFFF">{titulo}</h1>
  </td></tr>
  <tr><td style="background:{DOURADO};height:4px;line-height:4px;font-size:0">&nbsp;</td></tr>
{corpo}
  <tr><td style="background:{MARINHO};padding:26px 32px">
    <p style="margin:0 0 10px;font-size:16px;font-weight:700;line-height:1.4;color:#FFFFFF">&ldquo;Seus direitos no trabalho, explicados em linguagem simples.&rdquo;</p>
    <p style="margin:0 0 10px;font-size:13px;line-height:1.5;color:#B8BED3">Respostas baseadas na Cartilha de Direitos e Obrigações no Trabalho do TRT4, sempre com a fonte.</p>
    {rodape_extra}
    <p style="margin:0;font-size:12px;line-height:1.5;color:#8C93AD">{AVISO}</p>
  </td></tr>

</table>
</td></tr>
</table>
</body>
</html>"""


def _lista_texto(titulo, itens):
    if not itens:
        return []
    return ["", titulo] + [f"- {i['titulo']}\n  {i['url']}" for i in itens]


def montar_email_conteudo(nome, pergunta, resposta, materiais):
    """Resposta da cartilha com os sites e vídeos sobre o assunto."""
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
    corpo = f"""
  <tr><td style="padding:30px 32px 6px">
    <p style="margin:0 0 16px;font-size:16px;font-weight:700;color:{MARINHO}">Olá, {escape(nome)}!</p>
    {_rotulo("O que diz a cartilha")}
    {_paragrafos(resposta)}
  </td></tr>
  {_secao_links("Para ler mais", materiais["sites"], "&#8599;", MARINHO, DOURADO)}
  {_secao_links("Vídeos sobre o assunto", materiais["videos"], "&#9654;", DOURADO, MARINHO)}
  <tr><td style="padding:0 32px 28px">
    <p style="margin:0;padding:14px 16px;border-radius:12px;background:{FUNDO_SUAVE};font-size:14px;line-height:1.5;color:{TEXTO_SUAVE}">
      Ficou com outra dúvida? Volte ao Oráculo e pergunte do seu jeito: a resposta vem em linguagem simples e com a fonte.
    </p>
  </td></tr>
"""
    return {
        "assunto": "Oráculo: mais sobre a sua pergunta",
        "texto": "\n".join(texto),
        "html": _html(resposta[:120], "Sua pergunta", escape(pergunta), corpo),
    }


def montar_email_atualizacao(tema, titulo, conteudo, url):
    """Novidade sobre um tema que a pessoa acompanha."""
    texto = [titulo, "", conteudo]
    botao = ""
    if url:
        texto += ["", f"Saiba mais: {url}"]
        botao = (
            f'<a href="{escape(url)}" style="display:inline-block;margin-top:6px;padding:12px 22px;border-radius:10px;'
            f'background:{MARINHO};color:#FFFFFF;font-size:15px;font-weight:700;text-decoration:none">Saiba mais</a>'
        )
    rodape = "Você recebe este e-mail porque acompanha este tema no Oráculo."
    texto += ["", rodape]
    corpo = f"""
  <tr><td style="padding:30px 32px">
    {_rotulo(f"Novidade sobre {escape(tema)}")}
    {_paragrafos(conteudo)}
    {botao}
  </td></tr>
"""
    rodape_html = f'<p style="margin:0 0 10px;font-size:13px;line-height:1.5;color:#B8BED3">{rodape}</p>'
    return {
        "assunto": f"Oráculo: novidade sobre {tema}",
        "texto": "\n".join(texto),
        "html": _html(conteudo[:120], f"Tema que você acompanha · {escape(tema)}", escape(titulo), corpo, rodape_html),
    }
