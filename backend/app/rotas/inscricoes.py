"""Acompanhamento de temas (UC06, RF12): cada usuário gerencia as próprias inscrições."""

from fastapi import APIRouter, Depends, HTTPException, Response

from app.dependencias import obter_repositorio, usuario_atual
from app.esquemas import Inscricao, NovaInscricao
from app.repositorio import RegistroDuplicado
from app.rotas.base_conhecimento import validar_tema
from app.telefone import TelefoneInvalido, normalizar_telefone

rotas = APIRouter(prefix="/api/inscricoes", tags=["Acompanhamento de temas"])


@rotas.get("", response_model=list[Inscricao])
def listar(usuario=Depends(usuario_atual), repositorio=Depends(obter_repositorio)):
    return repositorio.listar_inscricoes(usuario["id"])


@rotas.post("", response_model=Inscricao, status_code=201)
def criar(dados: NovaInscricao, usuario=Depends(usuario_atual), repositorio=Depends(obter_repositorio)):
    if not dados.consentimento:
        raise HTTPException(status_code=422, detail="É preciso autorizar o envio de atualizações pelo WhatsApp.")
    try:
        telefone = normalizar_telefone(dados.telefone)
    except TelefoneInvalido as erro:
        raise HTTPException(status_code=422, detail=str(erro))
    validar_tema(repositorio, dados.tema_id)
    try:
        return repositorio.criar_inscricao(usuario["id"], dados.tema_id, telefone)
    except RegistroDuplicado as erro:
        raise HTTPException(status_code=409, detail=str(erro))


@rotas.delete("/{inscricao_id}", status_code=204)
def excluir(inscricao_id: str, usuario=Depends(usuario_atual), repositorio=Depends(obter_repositorio)):
    if not repositorio.excluir_inscricao(usuario["id"], inscricao_id):
        raise HTTPException(status_code=404, detail="Inscrição não encontrada.")
    return Response(status_code=204)
