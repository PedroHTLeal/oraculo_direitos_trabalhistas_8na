"""Conexões com os serviços e controle de acesso.

Cada dependência é criada uma vez e pode ser substituída por uma versão falsa nos testes.
"""

import os
from datetime import datetime, timezone
from functools import lru_cache

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import ConfiguracaoAusente, carregar_configuracao
from app.ia import AssistenteIA
from app.repositorio import RepositorioSupabase
from app.seguranca import hash_token
from app.whatsapp import EnviadorMetaCloud, EnviadorTwilio


@lru_cache
def obter_configuracao():
    return carregar_configuracao()


@lru_cache
def obter_repositorio():
    config = obter_configuracao()
    return RepositorioSupabase(config.supabase_url, config.supabase_chave_servico)


@lru_cache
def obter_ia():
    if not os.getenv("GEMINI_API_KEY", "").strip():
        raise ConfiguracaoAusente("Variável GEMINI_API_KEY não configurada no arquivo backend/.env")
    return AssistenteIA()


@lru_cache
def obter_whatsapp():
    # O serviço de envio é escolhido no backend/.env (PROVEDOR_WHATSAPP)
    config = obter_configuracao()
    if config.provedor_whatsapp == "meta":
        if not (config.meta_token and config.meta_phone_number_id):
            raise ConfiguracaoAusente("WhatsApp Cloud API (Meta) não configurado no arquivo backend/.env")
        return EnviadorMetaCloud(config.meta_token, config.meta_phone_number_id, config.meta_versao_api)
    if not (config.twilio_account_sid and config.twilio_auth_token and config.twilio_whatsapp_numero):
        raise ConfiguracaoAusente("Twilio não configurado no arquivo backend/.env")
    return EnviadorTwilio(config.twilio_account_sid, config.twilio_auth_token, config.twilio_whatsapp_numero)


_bearer = HTTPBearer(auto_error=False)


def obter_token(credenciais: HTTPAuthorizationCredentials | None = Depends(_bearer)):
    if not credenciais:
        raise HTTPException(status_code=401, detail="Faça login para continuar.")
    return credenciais.credentials


def usuario_atual(token=Depends(obter_token), repositorio=Depends(obter_repositorio)):
    sessao = repositorio.obter_sessao(hash_token(token))
    if not sessao or datetime.fromisoformat(sessao["expira_em"]) < datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Sua sessão expirou. Faça login novamente.")
    usuario = sessao["usuario"]
    if not usuario["ativo"]:
        raise HTTPException(status_code=403, detail="Seu acesso foi desativado.")
    return usuario


def exigir_perfil(*perfis):
    """Libera a rota apenas para os perfis informados."""

    def verificar(usuario=Depends(usuario_atual)):
        if usuario["perfil"] not in perfis:
            raise HTTPException(status_code=403, detail="Você não tem permissão para acessar esta área.")
        return usuario

    return verificar


# Perfis de cada área (RF14, RNF04)
somente_administrador = exigir_perfil("administrador")
equipe_de_conteudo = exigir_perfil("administrador", "curador")
