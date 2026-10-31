import pytest

NOVO = {"nome": "Carlos Curador", "email": "carlos@oraculo.com.br", "senha": "senha-forte-1", "perfil": "curador"}


@pytest.mark.parametrize("perfil", ["curador", "usuario"])
def test_somente_administrador_gerencia_usuarios(client, falsos, entrar, perfil):
    cabecalho = entrar(perfil)

    assert client.get("/api/usuarios", headers=cabecalho).status_code == 403
    assert client.post("/api/usuarios", json=NOVO, headers=cabecalho).status_code == 403


def test_administrador_cria_lista_altera_e_exclui_usuario(client, falsos, entrar):
    cabecalho = entrar("administrador")

    criado = client.post("/api/usuarios", json=NOVO, headers=cabecalho)
    assert criado.status_code == 201
    usuario_id = criado.json()["id"]
    assert criado.json()["perfil"] == "curador"

    assert "carlos@oraculo.com.br" in [u["email"] for u in client.get("/api/usuarios", headers=cabecalho).json()]

    alterado = client.put(f"/api/usuarios/{usuario_id}", json={"perfil": "administrador"}, headers=cabecalho)
    assert alterado.json()["perfil"] == "administrador"

    assert client.delete(f"/api/usuarios/{usuario_id}", headers=cabecalho).status_code == 204
    assert client.put(f"/api/usuarios/{usuario_id}", json={"nome": "Xavier"}, headers=cabecalho).status_code == 404


def test_perfil_invalido_e_rejeitado(client, falsos, entrar):
    resposta = client.post("/api/usuarios", json={**NOVO, "perfil": "dono"}, headers=entrar("administrador"))
    assert resposta.status_code == 422
    assert resposta.json()["detail"] == "Escolha um perfil válido."


def test_nao_permite_ficar_sem_administrador(client, falsos, entrar):
    cabecalho = entrar("administrador", email="admin@oraculo.com.br")
    eu = client.get("/api/auth/eu", headers=cabecalho).json()

    rebaixar = client.put(f"/api/usuarios/{eu['id']}", json={"perfil": "curador"}, headers=cabecalho)
    excluir = client.delete(f"/api/usuarios/{eu['id']}", headers=cabecalho)

    assert rebaixar.status_code == excluir.status_code == 422
    assert rebaixar.json()["detail"] == "O sistema precisa de pelo menos um administrador ativo."


def test_desativar_usuario_encerra_as_sessoes_dele(client, falsos, entrar):
    admin = entrar("administrador")
    curador = entrar("curador", email="curador@oraculo.com.br")
    curador_id = falsos[0].obter_usuario_por_email("curador@oraculo.com.br")["id"]

    client.put(f"/api/usuarios/{curador_id}", json={"ativo": False}, headers=admin)

    assert client.get("/api/auth/eu", headers=curador).status_code == 401


def test_email_repetido_ao_alterar(client, falsos, entrar):
    cabecalho = entrar("administrador")
    client.post("/api/usuarios", json=NOVO, headers=cabecalho)
    outro = client.post("/api/usuarios", json={**NOVO, "email": "outro@oraculo.com.br"}, headers=cabecalho).json()

    resposta = client.put(f"/api/usuarios/{outro['id']}", json={"email": "carlos@oraculo.com.br"}, headers=cabecalho)

    assert resposta.status_code == 409
