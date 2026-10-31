from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict, Field

from app.sugestoes import SUGESTOES

app = FastAPI(title="Oráculo dos Direitos Trabalhistas")


class Pergunta(BaseModel):
    # Remove espaços das pontas antes de validar o tamanho
    model_config = ConfigDict(str_strip_whitespace=True)

    texto: str = Field(min_length=3, max_length=500)


class Fonte(BaseModel):
    titulo: str
    trecho: str
    url: str | None = None


class Resposta(BaseModel):
    pergunta: str
    resposta: str
    encontrou: bool
    fontes: list[Fonte]


@app.get("/api/saude")
def saude():
    return {"status": "ok"}


@app.get("/api/sugestoes")
def sugestoes():
    return SUGESTOES


@app.post("/api/perguntas", response_model=Resposta)
def perguntar(pergunta: Pergunta):
    # Resposta provisória até a implementação do RAG (PB06): o sistema
    # informa que não encontrou informações suficientes (RF09).
    return Resposta(
        pergunta=pergunta.texto,
        resposta=(
            "Ainda não encontrei informações suficientes na base de "
            "conhecimento para responder a essa pergunta. A base está em "
            "construção e novas respostas serão adicionadas em breve."
        ),
        encontrou=False,
        fontes=[],
    )
