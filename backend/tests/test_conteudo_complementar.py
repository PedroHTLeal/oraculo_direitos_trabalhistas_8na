MATERIAL = {
    "tema_id": 2,
    "assunto": "Estágio",
    "palavras_chave": ["Estágio", " estagiário ", "estagio"],
    "tipo": "video",
    "titulo": "Direitos do estagiário",
    "url": "https://www.youtube.com/watch?v=xyz",
    "ordem": 1,
}


def test_equipe_gerencia_os_sinonimos(client, falsos, entrar):
    repositorio = falsos[0]
    cabecalho = entrar("curador")

    criado = client.post("/api/sinonimos", json={"termo": "Salário Atrasado", "equivalentes": "Atraso de Salário"}, headers=cabecalho)
    assert criado.status_code == 201
    # Sem acentos e em minúsculas, como a busca compara
    assert criado.json() == {"termo": "salario atrasado", "equivalentes": "atraso de salario"}

    alterado = client.put("/api/sinonimos/salario atrasado", json={"termo": "salario atrasado", "equivalentes": "mora salarial"}, headers=cabecalho)
    assert alterado.json()["equivalentes"] == "mora salarial"
    assert {"termo": "salario atrasado", "equivalentes": "mora salarial"} in client.get("/api/sinonimos", headers=cabecalho).json()

    assert client.delete("/api/sinonimos/salario atrasado", headers=cabecalho).status_code == 204
    assert "salario atrasado" not in repositorio.sinonimos
    assert repositorio.historico[-1]["entidade"] == "sinonimo"


def test_sinonimo_repetido_e_validacao(client, falsos, entrar):
    cabecalho = entrar("administrador")

    repetido = client.post("/api/sinonimos", json={"termo": "Patrão", "equivalentes": "empregador"}, headers=cabecalho)
    curto = client.post("/api/sinonimos", json={"termo": "a", "equivalentes": "b"}, headers=cabecalho)

    assert repetido.status_code == 409
    assert repetido.json()["detail"] == 'A palavra "patrao" já está cadastrada.'
    assert curto.status_code == 422


def test_usuario_comum_nao_acessa(client, falsos, entrar):
    cabecalho = entrar("usuario")
    assert client.get("/api/sinonimos", headers=cabecalho).status_code == 403
    assert client.get("/api/materiais", headers=cabecalho).status_code == 403


def test_equipe_cadastra_e_altera_sites_e_videos(client, falsos, entrar):
    cabecalho = entrar("curador")

    criado = client.post("/api/materiais", json=MATERIAL, headers=cabecalho)
    assert criado.status_code == 201
    material = criado.json()
    assert material["tema"] == "Contrato de Estágio"
    # Palavras-chave sem acento, minúsculas e sem repetição
    assert material["palavras_chave"] == ["estagio", "estagiario"]

    alterado = client.put(f"/api/materiais/{material['id']}", json={**MATERIAL, "titulo": "Novo título"}, headers=cabecalho)
    assert alterado.json()["titulo"] == "Novo título"
    assert client.delete(f"/api/materiais/{material['id']}", headers=cabecalho).status_code == 204
    assert client.delete(f"/api/materiais/{material['id']}", headers=cabecalho).status_code == 404


def test_validacoes_dos_materiais(client, falsos, entrar):
    cabecalho = entrar("curador")

    video_sem_youtube = client.post("/api/materiais", json={**MATERIAL, "url": "https://www.exemplo.com.br/video"}, headers=cabecalho)
    sem_palavras = client.post("/api/materiais", json={**MATERIAL, "palavras_chave": ["  "]}, headers=cabecalho)
    tema_invalido = client.post("/api/materiais", json={**MATERIAL, "tema_id": 99}, headers=cabecalho)
    client.post("/api/materiais", json=MATERIAL, headers=cabecalho)
    repetido = client.post("/api/materiais", json=MATERIAL, headers=cabecalho)

    assert video_sem_youtube.json()["detail"] == "Para vídeos, use o link de um vídeo do YouTube."
    assert sem_palavras.json()["detail"] == "Informe pelo menos uma palavra-chave."
    assert tema_invalido.status_code == 422
    assert repetido.status_code == 409


def test_material_cadastrado_vai_no_saiba_mais(client, falsos, entrar):
    _, _, email = falsos
    client.post("/api/materiais", json={**MATERIAL, "palavras_chave": ["ferias"], "assunto": "Férias"}, headers=entrar("curador"))
    pergunta_id = client.post("/api/perguntas", json={"texto": "Quantos dias de férias eu tenho?"}).json()["id"]

    client.post(
        "/api/saiba-mais",
        json={"pergunta_id": pergunta_id, "nome": "Maria", "email": "maria@exemplo.com.br", "consentimento": True},
    )

    assert "https://www.youtube.com/watch?v=xyz" in email.enviados[0][1]["texto"]
