"""Consulta pública: perguntas, respostas e conteúdo complementar pelo WhatsApp.
Não exige login (RF01)."""

import logging

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from google.genai import errors as erros_gemini

from app.dependencias import obter_configuracao, obter_ia, obter_repositorio, obter_whatsapp, usuario_atual
from app.esquemas import Fonte, PedidoSaibaMais, Pergunta, Resposta, SituacaoPedido
from app.ia import RecusaDaIA
from app.sugestoes import SUGESTOES
from app.whatsapp import montar_mensagem

logger = logging.getLogger("oraculo")
rotas = APIRouter(prefix="/api", tags=["Consulta"])

RESPOSTA_SEM_INFORMACAO = (
    "Não encontrei informações sobre isso na Cartilha de Direitos e Obrigações no Trabalho. "
    "Tente perguntar de outro jeito ou escolha um dos temas sugeridos."
)


@rotas.get("/sugestoes")
def sugestoes():
    return SUGESTOES


@rotas.get("/whatsapp")
def instrucoes_whatsapp(config=Depends(obter_configuracao)):
    # No Sandbox da Twilio, o celular precisa enviar um código antes de receber mensagens
    return {"numero": config.twilio_whatsapp_numero, "codigo": config.twilio_sandbox_codigo}


@rotas.post("/perguntas", response_model=Resposta)
def perguntar(pergunta: Pergunta, repositorio=Depends(obter_repositorio), ia=Depends(obter_ia)):
    trechos = repositorio.buscar_trechos(pergunta.texto)

    if not trechos:
        resultado = {"encontrou": False, "resposta": RESPOSTA_SEM_INFORMACAO, "trechos_usados": []}
    else:
        try:
            resultado = ia.responder(pergunta.texto, trechos)
        except RecusaDaIA:
            resultado = {"encontrou": False, "resposta": RESPOSTA_SEM_INFORMACAO, "trechos_usados": []}
        except erros_gemini.APIError:
            logger.exception("Falha ao gerar resposta com a IA")
            raise HTTPException(status_code=502, detail="Não foi possível gerar a resposta agora.")

    # A IA só pode citar trechos que foram realmente encontrados na busca
    por_id = {t["id"]: t for t in trechos}
    usados = [por_id[i] for i in resultado["trechos_usados"] if i in por_id] if resultado["encontrou"] else []

    pergunta_id = repositorio.salvar_pergunta(
        pergunta.texto, resultado["resposta"], resultado["encontrou"], [t["id"] for t in usados]
    )

    return Resposta(
        id=pergunta_id,
        pergunta=pergunta.texto,
        resposta=resultado["resposta"],
        encontrou=resultado["encontrou"],
        fontes=[
            Fonte(titulo=f"{t['tema']} · {t['secao']}", trecho=t["texto"], url=t["url"]) for t in usados
        ],
    )


@rotas.post("/saiba-mais", response_model=SituacaoPedido, status_code=202)
def saiba_mais(
    pedido: PedidoSaibaMais,
    tarefas: BackgroundTasks,
    usuario=Depends(usuario_atual),
    repositorio=Depends(obter_repositorio),
    ia=Depends(obter_ia),
    whatsapp=Depends(obter_whatsapp),
):
    # O conteúdo vai para o WhatsApp da conta, autorizado no cadastro (LGPD)
    telefone = usuario.get("telefone")
    if not telefone:
        raise HTTPException(status_code=422, detail="Sua conta não tem um telefone cadastrado para receber pelo WhatsApp.")

    pergunta = repositorio.obter_pergunta(pedido.pergunta_id)
    if not pergunta:
        raise HTTPException(status_code=404, detail="Pergunta não encontrada.")

    solicitacao_id = repositorio.criar_solicitacao(pedido.pergunta_id, telefone, usuario["id"])
    # A pesquisa de links e vídeos leva alguns segundos: roda depois de responder
    tarefas.add_task(enviar_conteudo_complementar, solicitacao_id, pergunta, telefone, repositorio, ia, whatsapp)
    return SituacaoPedido(id=solicitacao_id, status="pendente")


@rotas.get("/saiba-mais/{solicitacao_id}", response_model=SituacaoPedido)
def situacao_saiba_mais(solicitacao_id: str, repositorio=Depends(obter_repositorio)):
    solicitacao = repositorio.obter_solicitacao(solicitacao_id)
    if not solicitacao:
        raise HTTPException(status_code=404, detail="Pedido não encontrado.")
    return SituacaoPedido(id=solicitacao["id"], status=solicitacao["status"])


def enviar_conteudo_complementar(solicitacao_id, pergunta, telefone, repositorio, ia, whatsapp):
    try:
        trechos = repositorio.obter_trechos(pergunta["trechos_ids"])
        tema = trechos[0]["tema"] if trechos else pergunta["texto"]
        materiais = ia.buscar_materiais(pergunta["texto"], tema)
        whatsapp.enviar(telefone, montar_mensagem(pergunta["texto"], pergunta["resposta"], materiais))
        repositorio.concluir_solicitacao(solicitacao_id, materiais)
    except Exception as erro:  # registra qualquer falha para o pedido não ficar pendente
        logger.exception("Falha ao enviar conteúdo complementar %s", solicitacao_id)
        repositorio.registrar_erro_solicitacao(solicitacao_id, str(erro)[:500])
