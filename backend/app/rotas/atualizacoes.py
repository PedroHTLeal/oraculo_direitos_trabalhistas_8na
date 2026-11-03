"""Módulo 2 - atualizações de temas enviadas por e-mail (RF13, UC07).

A equipe publica uma novidade sobre um tema; o sistema envia um e-mail a cada
pessoa que acompanha o tema e guarda a situação de cada envio.
"""

import logging

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Response

from app.config import ConfiguracaoAusente
from app.dependencias import equipe_de_conteudo, obter_email, obter_repositorio, usuario_atual
from app.esquemas import Atualizacao, NovaAtualizacao
from app.historico import registrar
from app.rotas.base_conhecimento import validar_tema
from app.segundo_plano import agendar
from app.envio_email import montar_email_atualizacao

logger = logging.getLogger("oraculo")
rotas = APIRouter(prefix="/api", tags=["Atualizações"])


def email_opcional():
    # A atualização é publicada mesmo sem o e-mail configurado; os envios ficam com erro
    try:
        return obter_email()
    except ConfiguracaoAusente:
        return None


def enviar_atualizacao(atualizacao, envios, repositorio, enviador):
    mensagem = montar_email_atualizacao(
        atualizacao["tema"], atualizacao["titulo"], atualizacao["conteudo"], atualizacao["url"]
    )
    for envio in envios:
        try:
            if not enviador:
                raise ConfiguracaoAusente("E-mail não configurado")
            enviador.enviar(envio["email"], mensagem)
            repositorio.registrar_envio(atualizacao["id"], envio["inscricao_id"], "enviado")
        except Exception:
            logger.exception("Falha ao enviar a atualização %s", atualizacao["id"])
            repositorio.registrar_envio(atualizacao["id"], envio["inscricao_id"], "erro")


@rotas.get("/atualizacoes", response_model=list[Atualizacao])
def listar(tema_id: int | None = None, _=Depends(equipe_de_conteudo), repositorio=Depends(obter_repositorio)):
    return repositorio.listar_atualizacoes(tema_id)


@rotas.post("/atualizacoes", response_model=Atualizacao, status_code=201)
def publicar(
    dados: NovaAtualizacao,
    tarefas: BackgroundTasks,
    usuario=Depends(equipe_de_conteudo),
    repositorio=Depends(obter_repositorio),
    enviador=Depends(email_opcional),
):
    validar_tema(repositorio, dados.tema_id)
    atualizacao = repositorio.criar_atualizacao(dados.tema_id, dados.titulo, dados.conteudo, dados.url, usuario["id"])

    # Regra de negócio: só recebem as inscrições ativas do tema, no momento da publicação
    inscricoes = repositorio.listar_inscricoes_ativas(dados.tema_id)
    repositorio.criar_envios(atualizacao["id"], [i["id"] for i in inscricoes])
    envios = [{"inscricao_id": i["id"], "email": i["email"]} for i in inscricoes]
    agendar(tarefas, enviar_atualizacao, atualizacao, envios, repositorio, enviador)

    registrar(
        repositorio,
        usuario,
        "publicar",
        "atualizacao",
        atualizacao["id"],
        f'Publicou "{dados.titulo}" em {atualizacao["tema"]} para {len(inscricoes)} inscrito(s)',
    )
    return {**atualizacao, "envios": {"pendente": len(inscricoes), "enviado": 0, "erro": 0}}


@rotas.post("/atualizacoes/{atualizacao_id}/reenviar", response_model=Atualizacao)
def reenviar(
    atualizacao_id: int,
    tarefas: BackgroundTasks,
    usuario=Depends(equipe_de_conteudo),
    repositorio=Depends(obter_repositorio),
    enviador=Depends(email_opcional),
):
    atualizacao = repositorio.obter_atualizacao(atualizacao_id)
    if not atualizacao:
        raise HTTPException(status_code=404, detail="Atualização não encontrada.")
    falhas = repositorio.listar_envios(atualizacao_id, status="erro")
    if not falhas:
        raise HTTPException(status_code=422, detail="Não há envios com erro para reenviar.")
    agendar(tarefas, enviar_atualizacao, atualizacao, falhas, repositorio, enviador)
    registrar(repositorio, usuario, "reenviar", "atualizacao", atualizacao_id, f'Reenviou "{atualizacao["titulo"]}" a {len(falhas)} inscrito(s)')
    return atualizacao


@rotas.delete("/atualizacoes/{atualizacao_id}", status_code=204)
def excluir(atualizacao_id: int, usuario=Depends(equipe_de_conteudo), repositorio=Depends(obter_repositorio)):
    atualizacao = repositorio.obter_atualizacao(atualizacao_id)
    if not atualizacao:
        raise HTTPException(status_code=404, detail="Atualização não encontrada.")
    # Regra de negócio: o curador só exclui as próprias publicações; o administrador, qualquer uma
    if usuario["perfil"] != "administrador" and atualizacao["autor_id"] != usuario["id"]:
        raise HTTPException(status_code=403, detail="Você só pode excluir as atualizações que publicou.")
    repositorio.excluir_atualizacao(atualizacao_id)
    registrar(repositorio, usuario, "excluir", "atualizacao", atualizacao_id, f'Excluiu a atualização "{atualizacao["titulo"]}"')
    return Response(status_code=204)


@rotas.get("/minhas-atualizacoes", response_model=list[Atualizacao])
def minhas_atualizacoes(usuario=Depends(usuario_atual), repositorio=Depends(obter_repositorio)):
    # Novidades dos temas que a pessoa acompanha, também visíveis no site
    return repositorio.atualizacoes_do_usuario(usuario["id"])
