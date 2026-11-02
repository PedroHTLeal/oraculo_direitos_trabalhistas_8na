"""Cadastro, login e logout.

O cadastro público é feito com nome, telefone (WhatsApp) e senha: a conta serve
para a pessoa receber conteúdos pelo WhatsApp. A equipe entra com o e-mail.
"""

from fastapi import APIRouter, Depends, HTTPException, Response

from app.dependencias import obter_repositorio, obter_token, usuario_atual
from app.esquemas import Cadastro, Login, Sessao, Usuario
from app.repositorio import RegistroDuplicado
from app.seguranca import expiracao_sessao, gerar_hash_senha, gerar_token, hash_token, verificar_senha
from app.telefone import TelefoneInvalido, normalizar_telefone

rotas = APIRouter(prefix="/api/auth", tags=["Autenticação"])

# Mensagem única para conta inexistente ou senha errada, para não revelar quais contas existem
CREDENCIAIS_INVALIDAS = "Telefone, e-mail ou senha incorretos."


def abrir_sessao(repositorio, usuario):
    token = gerar_token()
    repositorio.criar_sessao(hash_token(token), usuario["id"], expiracao_sessao())
    return Sessao(token=token, usuario=Usuario(**usuario))


def buscar_conta(repositorio, identificador):
    if "@" in identificador:
        return repositorio.obter_usuario_por_email(identificador)
    try:
        return repositorio.obter_usuario_por_telefone(normalizar_telefone(identificador))
    except TelefoneInvalido:
        return None


@rotas.post("/cadastro", response_model=Sessao, status_code=201)
def cadastrar(dados: Cadastro, repositorio=Depends(obter_repositorio)):
    if not dados.consentimento:
        raise HTTPException(status_code=422, detail="É preciso autorizar o envio de mensagens pelo WhatsApp.")
    try:
        telefone = normalizar_telefone(dados.telefone)
    except TelefoneInvalido as erro:
        raise HTTPException(status_code=422, detail=str(erro))
    # O cadastro público cria sempre o perfil "usuario"; outros perfis são dados pelo administrador
    try:
        usuario = repositorio.criar_usuario(
            dados.nome, None, telefone, gerar_hash_senha(dados.senha), "usuario", consentimento_whatsapp=True
        )
    except RegistroDuplicado as erro:
        raise HTTPException(status_code=409, detail=f"{erro} Se a conta é sua, use a opção Entrar.")
    return abrir_sessao(repositorio, usuario)


@rotas.post("/login", response_model=Sessao)
def entrar(dados: Login, repositorio=Depends(obter_repositorio)):
    usuario = buscar_conta(repositorio, dados.identificador)
    if not usuario or not verificar_senha(dados.senha, usuario["senha_hash"]):
        raise HTTPException(status_code=401, detail=CREDENCIAIS_INVALIDAS)
    if not usuario["ativo"]:
        raise HTTPException(status_code=403, detail="Seu acesso foi desativado. Procure um administrador.")
    return abrir_sessao(repositorio, {k: v for k, v in usuario.items() if k in Usuario.model_fields})


@rotas.post("/sair", status_code=204)
def sair(token=Depends(obter_token), repositorio=Depends(obter_repositorio)):
    repositorio.excluir_sessao(hash_token(token))
    return Response(status_code=204)


@rotas.get("/eu", response_model=Usuario)
def eu(usuario=Depends(usuario_atual)):
    return usuario
