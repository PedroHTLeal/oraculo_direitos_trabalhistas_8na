"""Gestão de usuários e perfis (somente administradores)."""

from fastapi import APIRouter, Depends, HTTPException, Response

from app.dependencias import obter_repositorio, somente_administrador
from app.esquemas import AlteracaoUsuario, NovoUsuario, Usuario
from app.repositorio import RegistroDuplicado
from app.seguranca import gerar_hash_senha

rotas = APIRouter(prefix="/api/usuarios", tags=["Usuários"])


@rotas.get("", response_model=list[Usuario])
def listar(_=Depends(somente_administrador), repositorio=Depends(obter_repositorio)):
    return repositorio.listar_usuarios()


@rotas.post("", response_model=Usuario, status_code=201)
def criar(dados: NovoUsuario, _=Depends(somente_administrador), repositorio=Depends(obter_repositorio)):
    try:
        usuario = repositorio.criar_usuario(dados.nome, dados.email, gerar_hash_senha(dados.senha), dados.perfil)
    except RegistroDuplicado as erro:
        raise HTTPException(status_code=409, detail=str(erro))
    return usuario


@rotas.put("/{usuario_id}", response_model=Usuario)
def alterar(
    usuario_id: str,
    dados: AlteracaoUsuario,
    administrador=Depends(somente_administrador),
    repositorio=Depends(obter_repositorio),
):
    atual = repositorio.obter_usuario(usuario_id)
    if not atual:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")

    campos = dados.model_dump(exclude_none=True)
    perde_administracao = atual["perfil"] == "administrador" and (
        campos.get("perfil", "administrador") != "administrador" or campos.get("ativo") is False
    )
    # Regra de negócio: o sistema nunca fica sem um administrador ativo
    if perde_administracao and atual["ativo"] and repositorio.contar_administradores_ativos() <= 1:
        raise HTTPException(status_code=422, detail="O sistema precisa de pelo menos um administrador ativo.")
    if usuario_id == administrador["id"] and perde_administracao:
        raise HTTPException(status_code=422, detail="Você não pode remover o seu próprio perfil de administrador.")

    if "senha" in campos:
        campos["senha_hash"] = gerar_hash_senha(campos.pop("senha"))
    try:
        usuario = repositorio.atualizar_usuario(usuario_id, campos)
    except RegistroDuplicado as erro:
        raise HTTPException(status_code=409, detail=str(erro))

    # Desativar ou trocar a senha encerra as sessões abertas desse usuário
    if campos.get("ativo") is False or "senha_hash" in campos:
        repositorio.excluir_sessoes_do_usuario(usuario_id)
    return usuario


@rotas.delete("/{usuario_id}", status_code=204)
def excluir(usuario_id: str, administrador=Depends(somente_administrador), repositorio=Depends(obter_repositorio)):
    if usuario_id == administrador["id"]:
        raise HTTPException(status_code=422, detail="Você não pode excluir a sua própria conta.")
    atual = repositorio.obter_usuario(usuario_id)
    if not atual:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    if atual["perfil"] == "administrador" and atual["ativo"] and repositorio.contar_administradores_ativos() <= 1:
        raise HTTPException(status_code=422, detail="O sistema precisa de pelo menos um administrador ativo.")
    repositorio.excluir_usuario(usuario_id)
    return Response(status_code=204)
