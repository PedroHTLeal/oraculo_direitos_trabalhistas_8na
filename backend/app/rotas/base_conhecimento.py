"""CRUD da base de conhecimento (UC07) e auditoria das perguntas (UC08).

Acesso: administradores e curadores.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Response

from app.dependencias import equipe_de_conteudo, obter_repositorio
from app.esquemas import DadosTrecho, PaginaTrechos, PerguntaRegistrada, Tema, Trecho
from app.historico import registrar

rotas = APIRouter(prefix="/api", tags=["Base de conhecimento"])


@rotas.get("/temas", response_model=list[Tema])
def listar_temas(repositorio=Depends(obter_repositorio)):
    # Lista pública: usada no painel e no acompanhamento de temas
    return repositorio.listar_temas()


def validar_tema(repositorio, tema_id):
    if tema_id not in {tema["id"] for tema in repositorio.listar_temas()}:
        raise HTTPException(status_code=422, detail="Escolha um tema válido.")


@rotas.get("/base/trechos", response_model=PaginaTrechos)
def listar_trechos(
    tema_id: int | None = None,
    busca: str | None = Query(default=None, max_length=100),
    pagina: int = Query(default=1, ge=1),
    por_pagina: int = Query(default=20, ge=1, le=100),
    _=Depends(equipe_de_conteudo),
    repositorio=Depends(obter_repositorio),
):
    itens, total = repositorio.listar_trechos(tema_id, (busca or "").strip() or None, pagina, por_pagina)
    return PaginaTrechos(itens=itens, total=total, pagina=pagina, por_pagina=por_pagina)


@rotas.get("/base/trechos/{trecho_id}", response_model=Trecho)
def obter_trecho(trecho_id: int, _=Depends(equipe_de_conteudo), repositorio=Depends(obter_repositorio)):
    trecho = repositorio.obter_trecho(trecho_id)
    if not trecho:
        raise HTTPException(status_code=404, detail="Trecho não encontrado.")
    return trecho


@rotas.post("/base/trechos", response_model=Trecho, status_code=201)
def criar_trecho(dados: DadosTrecho, usuario=Depends(equipe_de_conteudo), repositorio=Depends(obter_repositorio)):
    validar_tema(repositorio, dados.tema_id)
    trecho = repositorio.criar_trecho(dados.tema_id, dados.secao, dados.texto, usuario["id"])
    registrar(repositorio, usuario, "criar", "trecho", trecho["id"], f'Incluiu "{dados.secao}" em {trecho["tema"]}')
    return trecho


@rotas.put("/base/trechos/{trecho_id}", response_model=Trecho)
def atualizar_trecho(
    trecho_id: int,
    dados: DadosTrecho,
    usuario=Depends(equipe_de_conteudo),
    repositorio=Depends(obter_repositorio),
):
    validar_tema(repositorio, dados.tema_id)
    trecho = repositorio.atualizar_trecho(trecho_id, dados.tema_id, dados.secao, dados.texto, usuario["id"])
    if not trecho:
        raise HTTPException(status_code=404, detail="Trecho não encontrado.")
    registrar(repositorio, usuario, "alterar", "trecho", trecho_id, f'Alterou "{dados.secao}" em {trecho["tema"]}')
    return trecho


@rotas.delete("/base/trechos/{trecho_id}", status_code=204)
def excluir_trecho(trecho_id: int, usuario=Depends(equipe_de_conteudo), repositorio=Depends(obter_repositorio)):
    trecho = repositorio.obter_trecho(trecho_id)
    if not trecho or not repositorio.excluir_trecho(trecho_id):
        raise HTTPException(status_code=404, detail="Trecho não encontrado.")
    registrar(repositorio, usuario, "excluir", "trecho", trecho_id, f'Excluiu "{trecho["secao"]}" de {trecho["tema"]}')
    return Response(status_code=204)


@rotas.get("/base/perguntas", response_model=list[PerguntaRegistrada])
def listar_perguntas(_=Depends(equipe_de_conteudo), repositorio=Depends(obter_repositorio)):
    # Auditoria (UC08): mostra só o texto e o resultado, sem dados pessoais
    return repositorio.listar_perguntas()
