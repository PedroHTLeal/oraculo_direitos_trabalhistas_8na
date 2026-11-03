import pytest

from app.envio_email import montar_email_atualizacao

NOVA = {
    "tema_id": 1,
    "titulo": "Novo prazo para as férias",
    "conteudo": "A cartilha foi atualizada com novas orientações sobre o pagamento das férias.",
    "url": "https://www.trt4.jus.br/portais/trt4/ferias",
}


def inscrever(client, entrar, tema_id=1, email="ana@exemplo.com.br"):
    cabecalho = entrar("usuario", login=email)
    client.post("/api/inscricoes", json={"tema_id": tema_id}, headers=cabecalho)
    return cabecalho


def test_publicar_envia_aos_inscritos_do_tema(client, falsos, entrar):
    _, _, email = falsos
    inscrever(client, entrar, 1, "ana@exemplo.com.br")
    inscrever(client, entrar, 1, "bia@exemplo.com.br")
    inscrever(client, entrar, 2, "caio@exemplo.com.br")  # outro tema: não recebe

    resposta = client.post("/api/atualizacoes", json=NOVA, headers=entrar("curador"))

    assert resposta.status_code == 201
    assert sorted(d for d, _ in email.enviados) == ["ana@exemplo.com.br", "bia@exemplo.com.br"]
    assert email.enviados[0][1]["assunto"] == "Oráculo: novidade sobre Férias"
    assert "Novo prazo para as férias" in email.enviados[0][1]["texto"]
    lista = client.get("/api/atualizacoes", headers=entrar("curador")).json()
    assert lista[0]["envios"] == {"pendente": 0, "enviado": 2, "erro": 0}


def test_sem_email_configurado_publica_e_marca_erro(client, falsos, entrar):
    from app.main import app
    from app.rotas.atualizacoes import email_opcional

    app.dependency_overrides[email_opcional] = lambda: None
    inscrever(client, entrar)
    cabecalho = entrar("curador")

    client.post("/api/atualizacoes", json=NOVA, headers=cabecalho)

    assert client.get("/api/atualizacoes", headers=cabecalho).json()[0]["envios"] == {"pendente": 0, "enviado": 0, "erro": 1}


def test_reenviar_so_os_envios_com_erro(client, falsos, entrar):
    repositorio, _, email = falsos
    inscrever(client, entrar)
    cabecalho = entrar("curador")
    atualizacao = client.post("/api/atualizacoes", json=NOVA, headers=cabecalho).json()

    sem_falhas = client.post(f"/api/atualizacoes/{atualizacao['id']}/reenviar", headers=cabecalho)
    assert sem_falhas.status_code == 422
    assert sem_falhas.json()["detail"] == "Não há envios com erro para reenviar."

    repositorio.envios[0]["status"] = "erro"
    assert client.post(f"/api/atualizacoes/{atualizacao['id']}/reenviar", headers=cabecalho).status_code == 200
    assert len(email.enviados) == 2
    assert repositorio.envios[0]["status"] == "enviado"


def test_curador_so_exclui_as_proprias_publicacoes(client, falsos, entrar):
    autor = entrar("curador")
    atualizacao = client.post("/api/atualizacoes", json=NOVA, headers=autor).json()

    outro_curador = client.delete(f"/api/atualizacoes/{atualizacao['id']}", headers=entrar("curador"))
    assert outro_curador.status_code == 403
    assert outro_curador.json()["detail"] == "Você só pode excluir as atualizações que publicou."

    assert client.delete(f"/api/atualizacoes/{atualizacao['id']}", headers=entrar("administrador")).status_code == 204


def test_validacoes_da_atualizacao(client, falsos, entrar):
    cabecalho = entrar("curador")

    curta = client.post("/api/atualizacoes", json={**NOVA, "conteudo": "curto"}, headers=cabecalho)
    link = client.post("/api/atualizacoes", json={**NOVA, "url": "www.site.com"}, headers=cabecalho)
    tema = client.post("/api/atualizacoes", json={**NOVA, "tema_id": 99}, headers=cabecalho)

    assert curta.json()["detail"] == "O campo conteúdo precisa ter pelo menos 20 caracteres."
    assert link.json()["detail"] == "O link precisa começar com http:// ou https://."
    assert tema.json()["detail"] == "Escolha um tema válido."


@pytest.mark.parametrize("perfil", ["usuario", None])
def test_somente_a_equipe_publica(client, falsos, entrar, perfil):
    cabecalho = entrar(perfil) if perfil else {}
    assert client.post("/api/atualizacoes", json=NOVA, headers=cabecalho).status_code in (401, 403)


def test_usuario_ve_as_novidades_dos_temas_que_acompanha(client, falsos, entrar):
    cabecalho = inscrever(client, entrar, 1)
    equipe = entrar("curador")
    client.post("/api/atualizacoes", json=NOVA, headers=equipe)
    client.post("/api/atualizacoes", json={**NOVA, "tema_id": 2, "titulo": "Novidade do estágio"}, headers=equipe)

    novidades = client.get("/api/minhas-atualizacoes", headers=cabecalho).json()

    assert [n["titulo"] for n in novidades] == ["Novo prazo para as férias"]


def test_email_da_atualizacao():
    email = montar_email_atualizacao("Férias", "Título", "Conteúdo da novidade", "https://exemplo.com")
    assert email["assunto"] == "Oráculo: novidade sobre Férias"
    assert "Saiba mais: https://exemplo.com" in email["texto"]
    assert 'href="https://exemplo.com"' in email["html"]
