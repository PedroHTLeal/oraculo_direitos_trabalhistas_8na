"""Cria o primeiro administrador do sistema (ou promove um usuário existente).

O cadastro pelo site cria apenas usuários comuns; os demais perfis são dados
por um administrador. Este script resolve o primeiro acesso.

Uso (na pasta backend/, com o .env preenchido):
    python scripts/criar_administrador.py
"""

import getpass
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pydantic import ValidationError  # noqa: E402

from app.config import carregar_configuracao  # noqa: E402
from app.esquemas import Cadastro  # noqa: E402
from app.repositorio import RepositorioSupabase  # noqa: E402
from app.seguranca import gerar_hash_senha  # noqa: E402


def main():
    config = carregar_configuracao()
    repositorio = RepositorioSupabase(config.supabase_url, config.supabase_chave_servico)

    nome = input("Nome: ").strip()
    email = input("E-mail: ").strip()
    senha = getpass.getpass("Senha (mínimo de 8 caracteres, não aparece na tela): ")
    if getpass.getpass("Repita a senha: ") != senha:
        sys.exit("As senhas não conferem.")

    try:
        dados = Cadastro(nome=nome, email=email, senha=senha)
    except ValidationError as erro:
        sys.exit("Dados inválidos: " + "; ".join(e["msg"] for e in erro.errors()))

    existente = repositorio.obter_usuario_por_email(dados.email)
    if existente:
        repositorio.atualizar_usuario(
            existente["id"], {"perfil": "administrador", "ativo": True, "senha_hash": gerar_hash_senha(dados.senha)}
        )
        print(f"{dados.email} agora é administrador.")
    else:
        repositorio.criar_usuario(dados.nome, dados.email, gerar_hash_senha(dados.senha), "administrador")
        print(f"Administrador {dados.email} criado.")


if __name__ == "__main__":
    main()
