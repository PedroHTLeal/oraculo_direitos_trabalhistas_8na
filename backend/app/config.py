import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")


class ConfiguracaoAusente(RuntimeError):
    pass


@dataclass(frozen=True)
class Configuracao:
    supabase_url: str
    supabase_chave_servico: str
    # Conta do Gmail que envia os e-mails e a senha de app dela
    email_remetente: str = ""
    email_senha_app: str = ""


def _ler(nome):
    valor = os.getenv(nome, "").strip()
    if not valor:
        raise ConfiguracaoAusente(f"Variável {nome} não configurada no arquivo backend/.env")
    return valor


def carregar_configuracao():
    return Configuracao(
        supabase_url=_ler("SUPABASE_URL"),
        supabase_chave_servico=_ler("SUPABASE_SERVICE_ROLE_KEY"),
        email_remetente=os.getenv("EMAIL_REMETENTE", "").strip(),
        # O Google mostra a senha de app em blocos separados por espaços
        email_senha_app=os.getenv("EMAIL_SENHA_APP", "").replace(" ", ""),
    )
