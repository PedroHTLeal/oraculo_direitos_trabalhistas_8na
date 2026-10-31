"""Senhas e tokens de sessão.

As senhas são guardadas com scrypt (biblioteca padrão do Python), com um sal
aleatório por usuário. O navegador recebe um token aleatório; o banco guarda
só o hash desse token, para que um vazamento do banco não permita entrar no sistema.
"""

import base64
import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone

PARAMETROS_SCRYPT = {"n": 2**14, "r": 8, "p": 1}
DURACAO_SESSAO = timedelta(hours=8)
TAMANHO_MINIMO_SENHA = 8


def _codificar(dados):
    return base64.b64encode(dados).decode("ascii")


def gerar_hash_senha(senha):
    sal = secrets.token_bytes(16)
    chave = hashlib.scrypt(senha.encode("utf-8"), salt=sal, **PARAMETROS_SCRYPT)
    p = PARAMETROS_SCRYPT
    return f"scrypt${p['n']}${p['r']}${p['p']}${_codificar(sal)}${_codificar(chave)}"


def verificar_senha(senha, hash_salvo):
    try:
        algoritmo, n, r, p, sal, chave = hash_salvo.split("$")
        if algoritmo != "scrypt":
            return False
        calculada = hashlib.scrypt(
            senha.encode("utf-8"), salt=base64.b64decode(sal), n=int(n), r=int(r), p=int(p)
        )
        return hmac.compare_digest(calculada, base64.b64decode(chave))
    except (ValueError, TypeError):
        return False


def gerar_token():
    return secrets.token_urlsafe(32)


def hash_token(token):
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def expiracao_sessao():
    return datetime.now(timezone.utc) + DURACAO_SESSAO
