import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.config import ConfiguracaoAusente
from app.rotas import autenticacao, base_conhecimento, consulta, inscricoes, usuarios

# Registro de erros (RNF06)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("oraculo")

app = FastAPI(title="Oráculo dos Direitos Trabalhistas")

for modulo in (consulta, autenticacao, usuarios, base_conhecimento, inscricoes):
    app.include_router(modulo.rotas)


@app.get("/api/saude")
def saude():
    return {"status": "ok"}


@app.exception_handler(ConfiguracaoAusente)
def configuracao_ausente(_, erro):
    logger.error("Configuração ausente: %s", erro)
    return JSONResponse(status_code=503, content={"detail": "O serviço ainda não foi configurado."})


NOMES_DOS_CAMPOS = {
    "texto": "texto",
    "nome": "nome",
    "email": "e-mail",
    "senha": "senha",
    "telefone": "telefone",
    "secao": "subtítulo",
    "tema_id": "tema",
    "perfil": "perfil",
}


def traduzir_erro(erro):
    """Transforma o erro técnico de validação em uma frase para o usuário (Sprint 04)."""
    campo = NOMES_DOS_CAMPOS.get(str(erro["loc"][-1]), str(erro["loc"][-1]))
    contexto = erro.get("ctx") or {}
    tipo = erro["type"]
    if tipo == "missing":
        return f"Preencha o campo {campo}."
    if tipo == "string_too_short":
        return f"O campo {campo} precisa ter pelo menos {contexto.get('min_length')} caracteres."
    if tipo == "string_too_long":
        return f"O campo {campo} pode ter no máximo {contexto.get('max_length')} caracteres."
    if tipo == "value_error" and campo == "e-mail":
        return "Informe um e-mail válido, por exemplo nome@exemplo.com."
    if tipo == "literal_error":
        return f"Escolha um {campo} válido."
    return f"Verifique o campo {campo}."


@app.exception_handler(RequestValidationError)
def erro_de_validacao(_: Request, erro: RequestValidationError):
    mensagens = list(dict.fromkeys(traduzir_erro(e) for e in erro.errors()))
    return JSONResponse(status_code=422, content={"detail": " ".join(mensagens), "erros": mensagens})
