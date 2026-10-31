import logging
import os
from functools import lru_cache

from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException
from fastapi.responses import JSONResponse
from google.genai import errors as erros_gemini
from pydantic import BaseModel, ConfigDict, Field

from app.config import ConfiguracaoAusente, carregar_configuracao
from app.ia import AssistenteIA, RecusaDaIA
from app.repositorio import RepositorioSupabase
from app.sugestoes import SUGESTOES
from app.telefone import TelefoneInvalido, normalizar_telefone
from app.whatsapp import EnviadorWhatsApp, montar_mensagem

# Registro de erros (RNF06)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("oraculo")

app = FastAPI(title="Oráculo dos Direitos Trabalhistas")

RESPOSTA_SEM_INFORMACAO = (
    "Não encontrei informações sobre isso na Cartilha de Direitos e Obrigações no Trabalho. "
    "Tente perguntar de outro jeito ou escolha um dos temas sugeridos."
)


# Dependências: criadas uma vez e substituídas por versões falsas nos testes


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
    config = obter_configuracao()
    if not (config.twilio_account_sid and config.twilio_auth_token and config.twilio_whatsapp_numero):
        raise ConfiguracaoAusente("Twilio não configurado no arquivo backend/.env")
    return EnviadorWhatsApp(config.twilio_account_sid, config.twilio_auth_token, config.twilio_whatsapp_numero)


@app.exception_handler(ConfiguracaoAusente)
def configuracao_ausente(_, erro):
    logger.error("Configuração ausente: %s", erro)
    return JSONResponse(status_code=503, content={"detail": "O serviço ainda não foi configurado."})


# Modelos da API


class Pergunta(BaseModel):
    # Remove espaços das pontas antes de validar o tamanho
    model_config = ConfigDict(str_strip_whitespace=True)

    texto: str = Field(min_length=3, max_length=500)


class Fonte(BaseModel):
    titulo: str
    trecho: str
    url: str | None = None


class Resposta(BaseModel):
    id: str | None = None
    pergunta: str
    resposta: str
    encontrou: bool
    fontes: list[Fonte]


class PedidoSaibaMais(BaseModel):
    pergunta_id: str
    telefone: str = Field(max_length=30)
    consentimento: bool


class SituacaoPedido(BaseModel):
    id: str
    status: str


# Rotas


@app.get("/api/saude")
def saude():
    return {"status": "ok"}


@app.get("/api/sugestoes")
def sugestoes():
    return SUGESTOES


@app.get("/api/whatsapp")
def instrucoes_whatsapp(config=Depends(obter_configuracao)):
    # No Sandbox da Twilio, o celular precisa enviar um código antes de receber mensagens
    return {"numero": config.twilio_whatsapp_numero, "codigo": config.twilio_sandbox_codigo}


@app.post("/api/perguntas", response_model=Resposta)
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


@app.post("/api/saiba-mais", response_model=SituacaoPedido, status_code=202)
def saiba_mais(
    pedido: PedidoSaibaMais,
    tarefas: BackgroundTasks,
    repositorio=Depends(obter_repositorio),
    ia=Depends(obter_ia),
    whatsapp=Depends(obter_whatsapp),
):
    if not pedido.consentimento:
        raise HTTPException(status_code=422, detail="É preciso autorizar o envio pelo WhatsApp.")
    try:
        telefone = normalizar_telefone(pedido.telefone)
    except TelefoneInvalido as erro:
        raise HTTPException(status_code=422, detail=str(erro))

    pergunta = repositorio.obter_pergunta(pedido.pergunta_id)
    if not pergunta:
        raise HTTPException(status_code=404, detail="Pergunta não encontrada.")

    solicitacao_id = repositorio.criar_solicitacao(pedido.pergunta_id, telefone)
    # A pesquisa de links e vídeos leva alguns segundos: roda depois de responder
    tarefas.add_task(enviar_conteudo_complementar, solicitacao_id, pergunta, telefone, repositorio, ia, whatsapp)
    return SituacaoPedido(id=solicitacao_id, status="pendente")


@app.get("/api/saiba-mais/{solicitacao_id}", response_model=SituacaoPedido)
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
