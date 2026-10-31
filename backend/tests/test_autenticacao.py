from app.seguranca import gerar_hash_senha, verificar_senha
from tests.conftest import expirar_sessoes


def test_hash_de_senha_confere_so_com_a_senha_certa():
    hash_salvo = gerar_hash_senha("minha-senha-123")

    assert hash_salvo.startswith("scrypt$")
    assert "minha-senha-123" not in hash_salvo
    assert verificar_senha("minha-senha-123", hash_salvo)
    assert not verificar_senha("outra-senha", hash_salvo)
    assert not verificar_senha("minha-senha-123", "hash-invalido")


def test_mesma_senha_gera_hashes_diferentes():
    assert gerar_hash_senha("igual-123456") != gerar_hash_senha("igual-123456")


def test_cadastro_cria_usuario_comum_e_ja_entra(client, falsos):
    resposta = client.post(
        "/api/auth/cadastro",
        json={"nome": "Maria Silva", "email": "Maria@Exemplo.com", "senha": "senha-forte-1", "perfil": "administrador"},
    )

    assert resposta.status_code == 201
    dados = resposta.json()
    # O perfil enviado é ignorado: o cadastro público sempre cria "usuario"
    assert dados["usuario"]["perfil"] == "usuario"
    assert dados["usuario"]["email"] == "maria@exemplo.com"
    assert "senha_hash" not in dados["usuario"]
    eu = client.get("/api/auth/eu", headers={"Authorization": f"Bearer {dados['token']}"})
    assert eu.json()["nome"] == "Maria Silva"


def test_cadastro_com_email_repetido(client, falsos):
    corpo = {"nome": "Maria", "email": "maria@exemplo.com", "senha": "senha-forte-1"}
    client.post("/api/auth/cadastro", json=corpo)

    resposta = client.post("/api/auth/cadastro", json=corpo)

    assert resposta.status_code == 409
    assert resposta.json()["detail"] == "Já existe um usuário com este e-mail."


def test_cadastro_valida_campos_com_mensagens_claras(client, falsos):
    resposta = client.post("/api/auth/cadastro", json={"nome": "M", "email": "nao-e-email", "senha": "123"})

    assert resposta.status_code == 422
    erros = resposta.json()["erros"]
    assert "O campo nome precisa ter pelo menos 2 caracteres." in erros
    assert "Informe um e-mail válido, por exemplo nome@exemplo.com." in erros
    assert "O campo senha precisa ter pelo menos 8 caracteres." in erros


def test_campo_obrigatorio_ausente(client, falsos):
    resposta = client.post("/api/auth/login", json={"email": "maria@exemplo.com"})
    assert resposta.json()["detail"] == "Preencha o campo senha."


def test_login_com_senha_errada_ou_email_inexistente(client, falsos, entrar):
    entrar("curador", email="curador@oraculo.com.br")

    errada = client.post("/api/auth/login", json={"email": "curador@oraculo.com.br", "senha": "senha-errada"})
    inexistente = client.post("/api/auth/login", json={"email": "ninguem@oraculo.com.br", "senha": "qualquer-1"})

    # A mesma mensagem nos dois casos, para não revelar quais e-mails existem
    assert errada.status_code == inexistente.status_code == 401
    assert errada.json()["detail"] == inexistente.json()["detail"] == "E-mail ou senha incorretos."


def test_usuario_desativado_nao_entra(client, falsos, entrar):
    repositorio = falsos[0]
    entrar("curador", email="curador@oraculo.com.br")
    usuario = repositorio.obter_usuario_por_email("curador@oraculo.com.br")
    repositorio.atualizar_usuario(usuario["id"], {"ativo": False})

    resposta = client.post("/api/auth/login", json={"email": "curador@oraculo.com.br", "senha": "senha-segura-123"})

    assert resposta.status_code == 403


def test_sair_encerra_a_sessao(client, falsos, entrar):
    cabecalho = entrar("usuario")

    assert client.post("/api/auth/sair", headers=cabecalho).status_code == 204
    assert client.get("/api/auth/eu", headers=cabecalho).status_code == 401


def test_sessao_expirada(client, falsos, entrar):
    cabecalho = entrar("usuario")
    expirar_sessoes(falsos[0])

    resposta = client.get("/api/auth/eu", headers=cabecalho)

    assert resposta.status_code == 401
    assert resposta.json()["detail"] == "Sua sessão expirou. Faça login novamente."


def test_rota_protegida_sem_login(client, falsos):
    resposta = client.get("/api/auth/eu")
    assert resposta.status_code == 401
    assert resposta.json()["detail"] == "Faça login para continuar."
