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
    twilio_account_sid: str
    twilio_auth_token: str
    twilio_whatsapp_numero: str
    twilio_sandbox_codigo: str


def _ler(nome):
    valor = os.getenv(nome, "").strip()
    if not valor:
        raise ConfiguracaoAusente(f"Variável {nome} não configurada no arquivo backend/.env")
    return valor


def carregar_configuracao():
    return Configuracao(
        supabase_url=_ler("SUPABASE_URL"),
        supabase_chave_servico=_ler("SUPABASE_SERVICE_ROLE_KEY"),
        twilio_account_sid=os.getenv("TWILIO_ACCOUNT_SID", "").strip(),
        twilio_auth_token=os.getenv("TWILIO_AUTH_TOKEN", "").strip(),
        twilio_whatsapp_numero=os.getenv("TWILIO_WHATSAPP_NUMERO", "").strip(),
        twilio_sandbox_codigo=os.getenv("TWILIO_SANDBOX_CODIGO", "").strip(),
    )
