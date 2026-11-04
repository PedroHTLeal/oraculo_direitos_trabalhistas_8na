"""Modelos de entrada e saída da API, validados pelo Pydantic."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.seguranca import TAMANHO_MINIMO_SENHA

Perfil = Literal["administrador", "curador", "usuario"]


class Entrada(BaseModel):
    # Remove espaços das pontas antes de validar o tamanho
    model_config = ConfigDict(str_strip_whitespace=True)


# Consulta pública


class Pergunta(Entrada):
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


class PedidoSaibaMais(Entrada):
    pergunta_id: str
    nome: str = Field(min_length=2, max_length=100)
    email: EmailStr
    consentimento: bool


class SituacaoPedido(BaseModel):
    id: str
    status: str


# Autenticação e usuários


class Cadastro(Entrada):
    """Cadastro público: a conta serve para acompanhar temas e receber as novidades por e-mail."""

    nome: str = Field(min_length=2, max_length=100)
    email: EmailStr
    senha: str = Field(min_length=TAMANHO_MINIMO_SENHA, max_length=128)
    consentimento: bool


class Login(Entrada):
    email: EmailStr
    senha: str = Field(min_length=1, max_length=128)


class Usuario(BaseModel):
    id: str
    nome: str
    email: str
    perfil: Perfil
    ativo: bool
    criado_em: str | None = None


class Sessao(BaseModel):
    token: str
    usuario: Usuario


class NovoUsuario(Entrada):
    """Cadastro feito pelo administrador."""

    nome: str = Field(min_length=2, max_length=100)
    email: EmailStr
    senha: str = Field(min_length=TAMANHO_MINIMO_SENHA, max_length=128)
    perfil: Perfil = "usuario"


class AlteracaoUsuario(Entrada):
    nome: str | None = Field(default=None, min_length=2, max_length=100)
    email: EmailStr | None = None
    perfil: Perfil | None = None
    ativo: bool | None = None
    senha: str | None = Field(default=None, min_length=TAMANHO_MINIMO_SENHA, max_length=128)


# Base de conhecimento (CRUD principal)


class Tema(BaseModel):
    id: int
    nome: str
    url: str


class DadosTrecho(Entrada):
    tema_id: int
    secao: str = Field(min_length=2, max_length=200)
    texto: str = Field(min_length=10, max_length=5000)


class Trecho(BaseModel):
    id: int
    tema_id: int
    tema: str
    secao: str
    ordem: int
    texto: str
    url: str
    atualizado_em: str | None = None


class PaginaTrechos(BaseModel):
    itens: list[Trecho]
    total: int
    pagina: int
    por_pagina: int


class PerguntaRegistrada(BaseModel):
    id: str
    texto: str
    encontrou: bool
    criado_em: str


# Acompanhamento de temas (perfil usuário)


class NovaInscricao(Entrada):
    # O e-mail vem da conta de quem está logado
    tema_id: int


class Inscricao(BaseModel):
    id: str
    tema_id: int
    tema: str
    email: str
    criado_em: str | None = None


# Atualizações de temas (Módulo 2)


class NovaAtualizacao(Entrada):
    tema_id: int
    titulo: str = Field(min_length=5, max_length=120)
    conteudo: str = Field(min_length=20, max_length=1000)
    url: str | None = Field(default=None, max_length=500, pattern=r"^https?://\S+$")


class Atualizacao(BaseModel):
    id: int
    tema_id: int
    tema: str
    titulo: str
    conteudo: str
    url: str | None = None
    autor_id: str | None = None
    autor: str | None = None
    publicado_em: str
    envios: dict[str, int]


# Sinônimos da busca e sites e vídeos do "Saber mais"


class DadosSinonimo(Entrada):
    termo: str = Field(min_length=2, max_length=60)
    equivalentes: str = Field(min_length=2, max_length=200)


class Sinonimo(BaseModel):
    termo: str
    equivalentes: str


class DadosMaterial(Entrada):
    tema_id: int
    assunto: str = Field(min_length=2, max_length=80)
    palavras_chave: list[str] = Field(min_length=1, max_length=10)
    tipo: Literal["site", "video"]
    titulo: str = Field(min_length=3, max_length=200)
    url: str = Field(max_length=500, pattern=r"^https?://\S+$")
    ordem: int = Field(default=1, ge=1, le=9)


class Material(BaseModel):
    id: int
    tema_id: int
    tema: str | None = None
    assunto: str
    palavras_chave: list[str]
    tipo: str
    titulo: str
    url: str
    ordem: int
