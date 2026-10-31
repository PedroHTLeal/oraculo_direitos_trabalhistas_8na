import pytest

TRECHO = {"tema_id": 1, "secao": "Férias coletivas", "texto": "A empresa pode dar férias coletivas a todos os empregados."}


def test_usuario_comum_nao_acessa_a_base(client, falsos, entrar):
    resposta = client.get("/api/base/trechos", headers=entrar("usuario"))
    assert resposta.status_code == 403
    assert resposta.json()["detail"] == "Você não tem permissão para acessar esta área."


def test_sem_login_nao_acessa_a_base(client, falsos):
    assert client.get("/api/base/trechos").status_code == 401


@pytest.mark.parametrize("perfil", ["administrador", "curador"])
def test_crud_completo_de_trechos(client, falsos, entrar, perfil):
    cabecalho = entrar(perfil)

    # Cadastrar
    criado = client.post("/api/base/trechos", json=TRECHO, headers=cabecalho)
    assert criado.status_code == 201
    trecho = criado.json()
    assert trecho["tema"] == "Férias"
    assert trecho["ordem"] == 2  # entra depois do trecho que já existia no tema

    # Consultar
    assert client.get(f"/api/base/trechos/{trecho['id']}", headers=cabecalho).json()["secao"] == "Férias coletivas"
    lista = client.get("/api/base/trechos", params={"tema_id": 1, "busca": "coletivas"}, headers=cabecalho).json()
    assert [t["id"] for t in lista["itens"]] == [trecho["id"]]
    assert lista["total"] == 1

    # Atualizar
    alterado = client.put(
        f"/api/base/trechos/{trecho['id']}", json={**TRECHO, "tema_id": 2, "secao": "Recesso"}, headers=cabecalho
    )
    assert alterado.json()["tema"] == "Contrato de Estágio"
    assert alterado.json()["secao"] == "Recesso"

    # Excluir
    assert client.delete(f"/api/base/trechos/{trecho['id']}", headers=cabecalho).status_code == 204
    assert client.get(f"/api/base/trechos/{trecho['id']}", headers=cabecalho).status_code == 404


def test_validacoes_do_trecho(client, falsos, entrar):
    cabecalho = entrar("curador")

    curto = client.post("/api/base/trechos", json={**TRECHO, "texto": "curto"}, headers=cabecalho)
    sem_secao = client.post("/api/base/trechos", json={"tema_id": 1, "texto": TRECHO["texto"]}, headers=cabecalho)
    tema_inexistente = client.post("/api/base/trechos", json={**TRECHO, "tema_id": 99}, headers=cabecalho)

    assert curto.json()["detail"] == "O campo texto precisa ter pelo menos 10 caracteres."
    assert sem_secao.json()["detail"] == "Preencha o campo subtítulo."
    assert tema_inexistente.json()["detail"] == "Escolha um tema válido."


def test_trecho_inexistente(client, falsos, entrar):
    cabecalho = entrar("curador")
    assert client.put("/api/base/trechos/999", json=TRECHO, headers=cabecalho).status_code == 404
    assert client.delete("/api/base/trechos/999", headers=cabecalho).status_code == 404


def test_auditoria_de_perguntas(client, falsos, entrar):
    client.post("/api/perguntas", json={"texto": "Quantos dias de férias?"})

    perguntas = client.get("/api/base/perguntas", headers=entrar("curador")).json()

    assert perguntas[0]["texto"] == "Quantos dias de férias?"
    assert set(perguntas[0]) == {"id", "texto", "encontrou", "criado_em"}


def test_lista_de_temas_e_publica(client, falsos):
    assert [t["nome"] for t in client.get("/api/temas").json()] == ["Férias", "Contrato de Estágio"]
