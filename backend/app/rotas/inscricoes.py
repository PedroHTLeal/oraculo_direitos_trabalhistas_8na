"""Acompanhamento de temas (UC06, RF12): cada usuário gerencia as próprias inscrições."""

from fastapi import APIRouter, Depends, HTTPException, Response

from app.dependencias import obter_repositorio, usuario_atual
from app.esquemas import Inscricao, NovaInscricao
from app.historico import registrar
from app.repositorio import RegistroDuplicado
from app.rotas.base_conhecimento import validar_tema

rotas = APIRouter(prefix="/api/inscricoes", tags=["Acompanhamento de temas"])


@rotas.get("", response_model=list[Inscricao])
def listar(usuario=Depends(usuario_atual), repositorio=Depends(obter_repositorio)):
    return repositorio.listar_inscricoes(usuario["id"])


@rotas.post("", response_model=Inscricao, status_code=201)
def criar(dados: NovaInscricao, usuario=Depends(usuario_atual), repositorio=Depends(obter_repositorio)):
    # As atualizações vão para o WhatsApp da conta, autorizado no cadastro (LGPD)
    if not usuario.get("telefone"):
        raise HTTPException(status_code=422, detail="Sua conta não tem um telefone cadastrado para receber pelo WhatsApp.")
    validar_tema(repositorio, dados.tema_id)
    try:
        inscricao = repositorio.criar_inscricao(usuario["id"], dados.tema_id, usuario["telefone"])
    except RegistroDuplicado as erro:
        raise HTTPException(status_code=409, detail=str(erro))
    registrar(repositorio, usuario, "criar", "inscricao", inscricao["id"], f"Passou a acompanhar {inscricao['tema']}")
    return inscricao


@rotas.delete("/{inscricao_id}", status_code=204)
def excluir(inscricao_id: str, usuario=Depends(usuario_atual), repositorio=Depends(obter_repositorio)):
    if not repositorio.excluir_inscricao(usuario["id"], inscricao_id):
        raise HTTPException(status_code=404, detail="Inscrição não encontrada.")
    registrar(repositorio, usuario, "excluir", "inscricao", inscricao_id, "Deixou de acompanhar um tema")
    return Response(status_code=204)
