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
    # Webhook do fluxo do n8n que envia o WhatsApp e o token combinado com ele
    n8n_webhook_url: str = ""
    n8n_token: str = ""


def _ler(nome):
    valor = os.getenv(nome, "").strip()
    if not valor:
        raise ConfiguracaoAusente(f"Variável {nome} não configurada no arquivo backend/.env")
    return valor


def carregar_configuracao():
    return Configuracao(
        supabase_url=_ler("SUPABASE_URL"),
        supabase_chave_servico=_ler("SUPABASE_SERVICE_ROLE_KEY"),
        n8n_webhook_url=os.getenv("N8N_WEBHOOK_URL", "").strip(),
        n8n_token=os.getenv("N8N_TOKEN", "").strip(),
    )
