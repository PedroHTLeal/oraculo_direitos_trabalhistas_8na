"""Cadastro, login e logout."""

from fastapi import APIRouter, Depends, HTTPException, Response

from app.dependencias import obter_repositorio, obter_token, usuario_atual
from app.esquemas import Cadastro, Login, Sessao, Usuario
from app.repositorio import RegistroDuplicado
from app.seguranca import expiracao_sessao, gerar_hash_senha, gerar_token, hash_token, verificar_senha

rotas = APIRouter(prefix="/api/auth", tags=["Autenticação"])

# Mensagem única para e-mail inexistente ou senha errada, para não revelar quais e-mails existem
CREDENCIAIS_INVALIDAS = "E-mail ou senha incorretos."


def abrir_sessao(repositorio, usuario):
    token = gerar_token()
    repositorio.criar_sessao(hash_token(token), usuario["id"], expiracao_sessao())
    return Sessao(token=token, usuario=Usuario(**usuario))


@rotas.post("/cadastro", response_model=Sessao, status_code=201)
def cadastrar(dados: Cadastro, repositorio=Depends(obter_repositorio)):
    # O cadastro público cria sempre o perfil "usuario"; outros perfis são dados pelo administrador
    try:
        usuario = repositorio.criar_usuario(dados.nome, dados.email, gerar_hash_senha(dados.senha), "usuario")
    except RegistroDuplicado as erro:
        raise HTTPException(status_code=409, detail=str(erro))
    return abrir_sessao(repositorio, usuario)


@rotas.post("/login", response_model=Sessao)
def entrar(dados: Login, repositorio=Depends(obter_repositorio)):
    usuario = repositorio.obter_usuario_por_email(dados.email)
    if not usuario or not verificar_senha(dados.senha, usuario["senha_hash"]):
        raise HTTPException(status_code=401, detail=CREDENCIAIS_INVALIDAS)
    if not usuario["ativo"]:
        raise HTTPException(status_code=403, detail="Seu acesso foi desativado. Procure um administrador.")
    return abrir_sessao(repositorio, usuario)


@rotas.post("/sair", status_code=204)
def sair(token=Depends(obter_token), repositorio=Depends(obter_repositorio)):
    repositorio.excluir_sessao(hash_token(token))
    return Response(status_code=204)


@rotas.get("/eu", response_model=Usuario)
def eu(usuario=Depends(usuario_atual)):
    return usuario
