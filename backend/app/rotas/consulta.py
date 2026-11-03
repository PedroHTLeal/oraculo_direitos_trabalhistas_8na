"""Consulta pública: perguntas, respostas e conteúdo complementar por e-mail.
Não exige login (RF01)."""

import logging
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from google.genai import errors as erros_gemini

from app.dependencias import obter_email, obter_ia, obter_repositorio
from app.esquemas import Fonte, PedidoSaibaMais, Pergunta, Resposta, SituacaoPedido
from app.historico import registrar
from app.ia import RecusaDaIA
from app.materiais import montar_materiais
from app.sugestoes import SUGESTOES
from app.envio_email import montar_email_conteudo

logger = logging.getLogger("oraculo")
rotas = APIRouter(prefix="/api", tags=["Consulta"])

# Limite de pedidos por e-mail em uma hora, para o formulário não virar fonte de spam
LIMITE_PEDIDOS_POR_HORA = 5

RESPOSTA_SEM_INFORMACAO = (
    "Não encontrei informações sobre isso na Cartilha de Direitos e Obrigações no Trabalho. "
    "Tente perguntar de outro jeito ou escolha um dos temas sugeridos."
)


@rotas.get("/sugestoes")
def sugestoes():
    return SUGESTOES


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
    repositorio=Depends(obter_repositorio),
    enviador=Depends(obter_email),
):
    # Não exige conta: basta o nome, o e-mail e a autorização de envio (LGPD)
    if not pedido.consentimento:
        raise HTTPException(status_code=422, detail="É preciso autorizar o envio do conteúdo para o seu e-mail.")

    pergunta = repositorio.obter_pergunta(pedido.pergunta_id)
    if not pergunta:
        raise HTTPException(status_code=404, detail="Pergunta não encontrada.")

    uma_hora_atras = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
    if repositorio.contar_solicitacoes_recentes(pedido.email, uma_hora_atras) >= LIMITE_PEDIDOS_POR_HORA:
        raise HTTPException(status_code=429, detail="Você fez muitos pedidos na última hora. Tente de novo mais tarde.")

    solicitacao_id = repositorio.criar_solicitacao(pedido.pergunta_id, pedido.nome, pedido.email)
    descricao = f'Pediu por e-mail mais conteúdo sobre "{pergunta["texto"][:80]}"'
    registrar(repositorio, {"id": None, "nome": pedido.nome}, "pedir_conteudo", "pergunta", pedido.pergunta_id, descricao)
    # A pesquisa de links e vídeos leva alguns segundos: roda depois de responder
    tarefas.add_task(enviar_conteudo_complementar, solicitacao_id, pergunta, pedido, repositorio, enviador)
    return SituacaoPedido(id=solicitacao_id, status="pendente")


@rotas.get("/saiba-mais/{solicitacao_id}", response_model=SituacaoPedido)
def situacao_saiba_mais(solicitacao_id: str, repositorio=Depends(obter_repositorio)):
    solicitacao = repositorio.obter_solicitacao(solicitacao_id)
    if not solicitacao:
        raise HTTPException(status_code=404, detail="Pedido não encontrado.")
    return SituacaoPedido(id=solicitacao["id"], status=solicitacao["status"])


def enviar_conteudo_complementar(solicitacao_id, pergunta, pedido, repositorio, enviador):
    try:
        trechos = repositorio.obter_trechos(pergunta["trechos_ids"])
        tema = trechos[0]["tema"] if trechos else "Direitos trabalhistas"
        url_cartilha = trechos[0]["url"] if trechos else None
        try:
            cadastrados = repositorio.listar_materiais()
        except Exception:  # sem a tabela de materiais, ainda envia a cartilha e a lei
            logger.exception("Não foi possível ler os materiais complementares")
            cadastrados = []
        materiais = montar_materiais(pergunta["texto"], tema, url_cartilha, cadastrados)
        conteudo = montar_email_conteudo(pedido.nome, pergunta["texto"], pergunta["resposta"], materiais)
        enviador.enviar(pedido.email, conteudo)
        repositorio.concluir_solicitacao(solicitacao_id, materiais)
    except Exception as erro:  # registra qualquer falha para o pedido não ficar pendente
        logger.exception("Falha ao enviar conteúdo complementar %s", solicitacao_id)
        repositorio.registrar_erro_solicitacao(solicitacao_id, str(erro)[:500])
