import smtplib

import pytest

from app.config import Configuracao
from app.dependencias import obter_email
from app.envio_email import EnviadorEmail, ErroEnvioEmail, montar_email_conteudo

MATERIAIS = {
    "sites": [{"titulo": "Férias <gov.br>", "url": "https://www.gov.br/ferias"}],
    "videos": [{"titulo": "Entenda suas férias", "url": "https://www.youtube.com/watch?v=abc"}],
}


class SmtpFalso:
    """Imita o smtplib.SMTP e guarda o que seria enviado."""

    ultimo = None

    def __init__(self, servidor, porta, timeout=None, falha=None):
        self.servidor, self.porta, self.falha = servidor, porta, falha
        self.etapas, self.enviada = [], None
        SmtpFalso.ultimo = self

    def __enter__(self):
        return self

    def __exit__(self, *erro):
        return False

    def starttls(self):
        self.etapas.append("starttls")

    def login(self, usuario, senha):
        if self.falha == "login":
            raise smtplib.SMTPAuthenticationError(535, b"Username and Password not accepted")
        self.etapas.append(("login", usuario, senha))

    def send_message(self, mensagem):
        self.enviada = mensagem


def test_envia_pelo_gmail_com_tls_e_senha_de_app():
    enviador = EnviadorEmail("oraculo@gmail.com", "abcdabcdabcdabcd", conectar=SmtpFalso)

    enviador.enviar("maria@exemplo.com.br", montar_email_conteudo("Maria", "Férias?", "Você tem 30 dias.", MATERIAIS))

    smtp = SmtpFalso.ultimo
    assert (smtp.servidor, smtp.porta) == ("smtp.gmail.com", 587)
    assert smtp.etapas == ["starttls", ("login", "oraculo@gmail.com", "abcdabcdabcdabcd")]
    assert smtp.enviada["To"] == "maria@exemplo.com.br"
    assert "oraculo@gmail.com" in smtp.enviada["From"]
    assert smtp.enviada["Subject"] == "Oráculo: mais sobre a sua pergunta"
    assert smtp.enviada.is_multipart()
    # O logo e a balança vão anexados ao e-mail e são referenciados pelo HTML
    anexos = {parte["Content-ID"] for parte in smtp.enviada.walk() if parte.get_content_type() == "image/png"}
    assert anexos == {"<simbolo@oraculo>", "<balanca@oraculo>"}


def test_login_recusado_vira_mensagem_clara():
    enviador = EnviadorEmail("oraculo@gmail.com", "errada", conectar=lambda *a, **k: SmtpFalso(*a, **k, falha="login"))

    with pytest.raises(ErroEnvioEmail, match="senha de app"):
        enviador.enviar("maria@exemplo.com.br", montar_email_conteudo("Maria", "P?", "R.", MATERIAIS))


def test_email_traz_resposta_sites_e_videos_com_html_seguro():
    conteudo = montar_email_conteudo("Maria", "Quantos dias de férias?", "Você tem 30 dias.", MATERIAIS)

    for parte in ("Olá, Maria!", "Você tem 30 dias.", "https://www.gov.br/ferias", "https://www.youtube.com/watch?v=abc"):
        assert parte in conteudo["texto"]
        assert parte in conteudo["html"]
    # Títulos vindos da pesquisa não podem injetar HTML no e-mail
    assert "Férias &lt;gov.br&gt;" in conteudo["html"]


def test_sem_configuracao_de_email_avisa(client, falsos, monkeypatch):
    from app import dependencias
    from app.main import app

    # Usa uma configuração sem e-mail, sem ler o backend/.env de verdade
    monkeypatch.setattr(dependencias, "obter_configuracao", lambda: Configuracao("https://exemplo.supabase.co", "chave"))
    obter_email.cache_clear()
    app.dependency_overrides.pop(obter_email)
    pergunta_id = client.post("/api/perguntas", json={"texto": "Quantos dias de férias?"}).json()["id"]

    resposta = client.post(
        "/api/saiba-mais",
        json={"pergunta_id": pergunta_id, "nome": "Maria", "email": "maria@exemplo.com.br", "consentimento": True},
    )

    assert resposta.status_code == 503
    obter_email.cache_clear()
