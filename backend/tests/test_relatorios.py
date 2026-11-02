from datetime import date, timedelta


def perguntar(client, falsos, texto, encontrou=True):
    falsos[1].resultado = {
        "encontrou": encontrou,
        "resposta": "Resposta." if encontrou else "A cartilha não trata disso.",
        "trechos_usados": [10] if encontrou else [],
    }
    client.post("/api/perguntas", json={"texto": texto})


def test_indicadores_do_dashboard(client, falsos, entrar):
    perguntar(client, falsos, "Quantos dias de férias?")
    perguntar(client, falsos, "Posso vender as férias?")
    perguntar(client, falsos, "Qual a capital da França?", encontrou=False)
    inscricao = entrar("usuario")
    client.post("/api/inscricoes", json={"tema_id": 1}, headers=inscricao)

    dados = client.get("/api/painel/indicadores", params={"dias": 7}, headers=entrar("curador")).json()

    assert dados["perguntas"] == {"total": 3, "respondidas": 2, "sem_resposta": 1, "taxa_resposta": 67}
    assert dados["temas_mais_consultados"] == [{"tema": "Férias", "total": 2}]
    assert dados["sem_resposta_recentes"][0]["texto"] == "Qual a capital da França?"
    assert dados["inscricoes"]["total"] == 1
    assert len(dados["perguntas_por_data"]) == 7
    assert sum(d["total"] for d in dados["perguntas_por_data"]) == 3


def test_periodo_do_dashboard_e_validado(client, falsos, entrar):
    resposta = client.get("/api/painel/indicadores", params={"dias": 15}, headers=entrar("curador"))
    assert resposta.status_code == 422


def test_relatorio_de_perguntas_com_filtros(client, falsos, entrar):
    perguntar(client, falsos, "Quantos dias de férias?")
    perguntar(client, falsos, "Qual a capital da França?", encontrou=False)
    cabecalho = entrar("curador")

    sem_resposta = client.get("/api/relatorios/perguntas", params={"resultado": "sem_resposta"}, headers=cabecalho).json()
    por_busca = client.get("/api/relatorios/perguntas", params={"busca": "férias"}, headers=cabecalho).json()
    por_tema = client.get("/api/relatorios/perguntas", params={"tema_id": 1}, headers=cabecalho).json()

    assert [p["texto"] for p in sem_resposta["itens"]] == ["Qual a capital da França?"]
    assert [p["texto"] for p in por_busca["itens"]] == ["Quantos dias de férias?"]
    assert por_tema["total"] == 1


def test_periodo_invertido_e_rejeitado(client, falsos, entrar):
    hoje = date.today()
    resposta = client.get(
        "/api/relatorios/perguntas",
        params={"inicio": hoje.isoformat(), "fim": (hoje - timedelta(days=3)).isoformat()},
        headers=entrar("curador"),
    )
    assert resposta.status_code == 422
    assert resposta.json()["detail"] == "A data final não pode ser anterior à data inicial."


def test_exportacao_em_csv(client, falsos, entrar):
    perguntar(client, falsos, "Quantos dias de férias?")

    resposta = client.get("/api/relatorios/perguntas", params={"formato": "csv"}, headers=entrar("curador"))

    assert resposta.headers["content-type"].startswith("text/csv")
    assert "attachment" in resposta.headers["content-disposition"]
    linhas = resposta.content.decode("utf-8-sig").splitlines()
    assert linhas[0] == "Data;Pergunta;Resultado;Temas"
    assert "Quantos dias de férias?;Respondida;Férias" in linhas[1]


def test_historico_registra_operacoes(client, falsos, entrar):
    admin = entrar("administrador")
    client.post("/api/base/trechos", json={"tema_id": 1, "secao": "Novo trecho", "texto": "Texto com mais de dez letras."}, headers=admin)

    historico = client.get("/api/relatorios/historico", headers=admin).json()
    acoes = [(h["acao"], h["entidade"]) for h in historico["itens"]]

    assert ("criar", "trecho") in acoes
    assert ("login", "conta") in acoes
    filtrado = client.get("/api/relatorios/historico", params={"acao": "criar"}, headers=admin).json()
    assert {h["acao"] for h in filtrado["itens"]} == {"criar"}
    csv = client.get("/api/relatorios/historico", params={"formato": "csv"}, headers=admin)
    assert csv.content.decode("utf-8-sig").startswith("Data;Usuário;Ação;Área;Descrição")


def test_historico_e_exclusivo_do_administrador(client, falsos, entrar):
    assert client.get("/api/relatorios/historico", headers=entrar("curador")).status_code == 403


def test_filtro_de_acao_invalido(client, falsos, entrar):
    resposta = client.get("/api/relatorios/historico", params={"acao": "hackear"}, headers=entrar("administrador"))
    assert resposta.json()["detail"] == "Escolha uma ação válida."


def test_falha_no_historico_nao_impede_a_operacao(client, falsos, entrar):
    def quebrar(*_):
        raise RuntimeError("banco indisponível")

    falsos[0].registrar_operacao = quebrar
    resposta = client.post(
        "/api/base/trechos",
        json={"tema_id": 1, "secao": "Novo trecho", "texto": "Texto com mais de dez letras."},
        headers=entrar("curador"),
    )
    assert resposta.status_code == 201
