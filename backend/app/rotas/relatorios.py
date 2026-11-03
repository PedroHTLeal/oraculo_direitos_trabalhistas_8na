"""Dashboard, relatórios com filtros, exportação em CSV e histórico (Sprint 07).

Acesso: administradores e curadores; o histórico de operações é só do administrador.
"""

import csv
import io
from collections import Counter
from datetime import date, datetime, time, timedelta, timezone
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Response

from app.dependencias import equipe_de_conteudo, obter_repositorio, somente_administrador
from app.historico import ACOES, ENTIDADES

rotas = APIRouter(prefix="/api", tags=["Dashboard e relatórios"])

FUSO = timezone(timedelta(hours=-3))  # horário de Brasília
Formato = Literal["json", "csv"]
PERIODOS = (7, 30, 90, 365)


def inicio_do_dia(dia):
    return datetime.combine(dia, time.min, tzinfo=FUSO).isoformat()


def periodo(inicio: date | None, fim: date | None):
    if inicio and fim and fim < inicio:
        raise HTTPException(status_code=422, detail="A data final não pode ser anterior à data inicial.")
    # A data final entra inteira no período
    return (inicio_do_dia(inicio) if inicio else None, inicio_do_dia(fim + timedelta(days=1)) if fim else None)


def data_local(texto):
    return datetime.fromisoformat(texto).astimezone(FUSO)


def exportar_csv(nome, cabecalho, linhas):
    saida = io.StringIO()
    # Separador ";" e marca UTF-8 para o Excel em português abrir com acentos corretos
    escritor = csv.writer(saida, delimiter=";")
    escritor.writerow(cabecalho)
    escritor.writerows(linhas)
    return Response(
        content="﻿" + saida.getvalue(),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{nome}-{date.today().isoformat()}.csv"'},
    )


def agrupar_por_data(perguntas, dias):
    """Perguntas por dia (até 31 dias), por semana (até 90) ou por mês."""
    hoje = datetime.now(FUSO).date()
    if dias <= 31:
        chaves = [hoje - timedelta(days=n) for n in range(dias - 1, -1, -1)]
        chave_de = lambda d: d  # noqa: E731
        rotulo = lambda d: d.strftime("%d/%m")  # noqa: E731
    elif dias <= 90:
        segunda = hoje - timedelta(days=hoje.weekday())
        chaves = [segunda - timedelta(weeks=n) for n in range(dias // 7, -1, -1)]
        chave_de = lambda d: d - timedelta(days=d.weekday())  # noqa: E731
        rotulo = lambda d: "sem. " + d.strftime("%d/%m")  # noqa: E731
    else:
        chaves = []
        mes = hoje.replace(day=1)
        for _ in range(12):
            chaves.insert(0, mes)
            mes = (mes - timedelta(days=1)).replace(day=1)
        chave_de = lambda d: d.replace(day=1)  # noqa: E731
        rotulo = lambda d: d.strftime("%m/%Y")  # noqa: E731

    totais = {chave: {"total": 0, "respondidas": 0} for chave in chaves}
    for pergunta in perguntas:
        chave = chave_de(data_local(pergunta["criado_em"]).date())
        if chave in totais:
            totais[chave]["total"] += 1
            totais[chave]["respondidas"] += int(pergunta["encontrou"])
    return [{"rotulo": rotulo(chave), **valores} for chave, valores in totais.items()]


@rotas.get("/painel/indicadores")
def indicadores(
    dias: int = 30,
    _=Depends(equipe_de_conteudo),
    repositorio=Depends(obter_repositorio),
):
    if dias not in PERIODOS:
        raise HTTPException(status_code=422, detail="Escolha um período válido: 7, 30, 90 ou 365 dias.")
    inicio = (datetime.now(FUSO) - timedelta(days=dias)).isoformat()
    perguntas = repositorio.perguntas_no_periodo(inicio=inicio)
    respondidas = sum(1 for p in perguntas if p["encontrou"])
    temas = Counter(tema for p in perguntas for tema in p["temas"])
    pedidos = Counter(s["status"] for s in repositorio.solicitacoes_no_periodo(inicio=inicio))
    inscricoes = Counter(i["temas"]["nome"] for i in repositorio.resumo_inscricoes())
    usuarios = Counter(u["perfil"] for u in repositorio.listar_usuarios() if u["ativo"])
    atualizacoes = [a for a in repositorio.listar_atualizacoes() if a["publicado_em"] >= inicio]

    return {
        "dias": dias,
        "perguntas": {
            "total": len(perguntas),
            "respondidas": respondidas,
            "sem_resposta": len(perguntas) - respondidas,
            "taxa_resposta": round(100 * respondidas / len(perguntas)) if perguntas else None,
        },
        "perguntas_por_data": agrupar_por_data(perguntas, dias),
        "temas_mais_consultados": [{"tema": t, "total": n} for t, n in temas.most_common(8)],
        "sem_resposta_recentes": [
            {"id": p["id"], "texto": p["texto"], "criado_em": p["criado_em"]} for p in perguntas if not p["encontrou"]
        ][:5],
        "saiba_mais": {status: pedidos.get(status, 0) for status in ("enviado", "pendente", "erro")},
        "inscricoes": {"total": sum(inscricoes.values()), "por_tema": [{"tema": t, "total": n} for t, n in inscricoes.most_common(8)]},
        "atualizacoes": {
            "publicadas": len(atualizacoes),
            "envios": sum(a["envios"]["enviado"] for a in atualizacoes),
            "falhas": sum(a["envios"]["erro"] for a in atualizacoes),
        },
        "usuarios": {perfil: usuarios.get(perfil, 0) for perfil in ("administrador", "curador", "usuario")},
    }


@rotas.get("/relatorios/perguntas")
def relatorio_perguntas(
    inicio: date | None = None,
    fim: date | None = None,
    resultado: Literal["respondida", "sem_resposta"] | None = None,
    tema_id: int | None = None,
    busca: str | None = Query(default=None, max_length=100),
    formato: Formato = "json",
    _=Depends(equipe_de_conteudo),
    repositorio=Depends(obter_repositorio),
):
    de, ate = periodo(inicio, fim)
    encontrou = None if resultado is None else resultado == "respondida"
    perguntas = repositorio.perguntas_no_periodo(de, ate, encontrou, (busca or "").strip() or None, tema_id)
    if formato == "csv":
        return exportar_csv(
            "perguntas",
            ["Data", "Pergunta", "Resultado", "Temas"],
            [
                [
                    data_local(p["criado_em"]).strftime("%d/%m/%Y %H:%M"),
                    p["texto"],
                    "Respondida" if p["encontrou"] else "Sem informação",
                    ", ".join(p["temas"]),
                ]
                for p in perguntas
            ],
        )
    return {"total": len(perguntas), "itens": perguntas}


@rotas.get("/relatorios/historico")
def relatorio_historico(
    inicio: date | None = None,
    fim: date | None = None,
    acao: str | None = None,
    entidade: str | None = None,
    busca: str | None = Query(default=None, max_length=100),
    formato: Formato = "json",
    _=Depends(somente_administrador),
    repositorio=Depends(obter_repositorio),
):
    if acao and acao not in ACOES:
        raise HTTPException(status_code=422, detail="Escolha uma ação válida.")
    if entidade and entidade not in ENTIDADES:
        raise HTTPException(status_code=422, detail="Escolha uma área válida.")
    de, ate = periodo(inicio, fim)
    registros = repositorio.listar_historico(de, ate, acao, entidade, (busca or "").strip() or None)
    if formato == "csv":
        return exportar_csv(
            "historico-de-operacoes",
            ["Data", "Usuário", "Ação", "Área", "Descrição"],
            [
                [
                    data_local(r["criado_em"]).strftime("%d/%m/%Y %H:%M"),
                    r["usuario_nome"] or "Visitante",
                    ACOES.get(r["acao"], r["acao"]),
                    ENTIDADES.get(r["entidade"], r["entidade"]),
                    r["descricao"],
                ]
                for r in registros
            ],
        )
    return {"total": len(registros), "itens": registros, "acoes": ACOES, "entidades": ENTIDADES}
