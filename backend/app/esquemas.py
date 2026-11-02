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
    # O telefone vem da conta de quem está logado
    pergunta_id: str


class SituacaoPedido(BaseModel):
    id: str
    status: str


# Autenticação e usuários


class Cadastro(Entrada):
    """Cadastro público: a conta serve para receber conteúdos pelo WhatsApp."""

    nome: str = Field(min_length=2, max_length=100)
    telefone: str = Field(min_length=8, max_length=30)
    senha: str = Field(min_length=TAMANHO_MINIMO_SENHA, max_length=128)
    consentimento: bool


class Login(Entrada):
    # Telefone (usuários) ou e-mail (equipe)
    identificador: str = Field(min_length=3, max_length=120)
    senha: str = Field(min_length=1, max_length=128)


class Usuario(BaseModel):
    id: str
    nome: str
    email: str | None = None
    telefone: str | None = None
    perfil: Perfil
    ativo: bool
    criado_em: str | None = None


class Sessao(BaseModel):
    token: str
    usuario: Usuario


class NovoUsuario(Entrada):
    """Cadastro feito pelo administrador: equipe com e-mail, usuários com telefone."""

    nome: str = Field(min_length=2, max_length=100)
    email: EmailStr | None = None
    telefone: str | None = Field(default=None, max_length=30)
    senha: str = Field(min_length=TAMANHO_MINIMO_SENHA, max_length=128)
    perfil: Perfil = "usuario"


class AlteracaoUsuario(Entrada):
    nome: str | None = Field(default=None, min_length=2, max_length=100)
    email: EmailStr | None = None
    telefone: str | None = Field(default=None, max_length=30)
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
    # O telefone vem da conta de quem está logado
    tema_id: int


class Inscricao(BaseModel):
    id: str
    tema_id: int
    tema: str
    telefone: str
    criado_em: str | None = None
