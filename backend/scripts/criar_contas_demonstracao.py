"""Cria uma conta de demonstração para cada perfil (administrador, curador, usuario).

As senhas são geradas aleatoriamente e gravadas no backend/.env (que não vai
para o GitHub), nas variáveis DEMO_<PERFIL>_LOGIN e DEMO_<PERFIL>_SENHA.
Se as contas já existirem, as senhas do .env são reaplicadas.

Uso (na pasta backend/):
    python scripts/criar_contas_demonstracao.py
"""

import secrets
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import dotenv_values, set_key  # noqa: E402

from app.config import carregar_configuracao  # noqa: E402
from app.repositorio import RepositorioSupabase  # noqa: E402
from app.seguranca import gerar_hash_senha  # noqa: E402

ARQUIVO_ENV = Path(__file__).resolve().parent.parent / ".env"

CONTAS = [
    ("administrador", "Ana Administradora", "admin.demo@example.com"),
    ("curador", "Carlos Curador", "curador.demo@example.com"),
    ("usuario", "Maria Trabalhadora", "usuario.demo@example.com"),
]


def main():
    config = carregar_configuracao()
    repositorio = RepositorioSupabase(config.supabase_url, config.supabase_chave_servico)
    variaveis = dotenv_values(ARQUIVO_ENV)

    for perfil, nome, email in CONTAS:
        chave = f"DEMO_{perfil.upper()}"
        senha = variaveis.get(f"{chave}_SENHA") or secrets.token_urlsafe(12)
        existente = repositorio.obter_usuario_por_email(email)
        if existente:
            repositorio.atualizar_usuario(
                existente["id"], {"perfil": perfil, "ativo": True, "senha_hash": gerar_hash_senha(senha)}
            )
        else:
            repositorio.criar_usuario(nome, email, gerar_hash_senha(senha), perfil, consentimento_email=perfil == "usuario")
        set_key(ARQUIVO_ENV, f"{chave}_LOGIN", email, quote_mode="never")
        set_key(ARQUIVO_ENV, f"{chave}_SENHA", senha, quote_mode="never")
        print(f"{perfil}: {email} (senha gravada em backend/.env)")


if __name__ == "__main__":
    main()
