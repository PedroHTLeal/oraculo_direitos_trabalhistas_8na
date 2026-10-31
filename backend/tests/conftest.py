import uuid
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

from app.config import Configuracao
from app.dependencias import obter_configuracao, obter_ia, obter_repositorio, obter_whatsapp
from app.ia import RecusaDaIA
from app.main import app
from app.repositorio import RegistroDuplicado
from app.seguranca import gerar_hash_senha

TRECHOS = [
    {
        "id": 10,
        "tema": "Férias",
        "secao": "Visão geral",
        "texto": "Todo(a) trabalhador(a) tem direito a 30 dias de férias depois de 12 meses.",
        "url": "https://www.trt4.jus.br/portais/trt4/ferias",
        "relevancia": 0.5,
    },
    {
        "id": 11,
        "tema": "Férias",
        "secao": "Pagamento das férias",
        "texto": "O valor das férias deve ser pago até 2 dias antes do início.",
        "url": "https://www.trt4.jus.br/portais/trt4/ferias",
        "relevancia": 0.3,
    },
]

TEMAS = [
    {"id": 1, "nome": "Férias", "url": "https://www.trt4.jus.br/portais/trt4/ferias"},
    {"id": 2, "nome": "Contrato de Estágio", "url": "https://www.trt4.jus.br/portais/trt4/contrato-de-estagio"},
]


def publico(usuario):
    return {k: v for k, v in usuario.items() if k != "senha_hash"}


class RepositorioFalso:
    def __init__(self):
        self.trechos = list(TRECHOS)
        self.perguntas = {}
        self.solicitacoes = {}
        self.usuarios = {}
        self.sessoes = {}
        self.inscricoes = {}
        self.base = {
            1: {"id": 1, "tema_id": 1, "secao": "Visão geral", "ordem": 1, "texto": "Todo trabalhador tem direito a 30 dias de férias."},
            2: {"id": 2, "tema_id": 2, "secao": "Direitos do estagiário", "ordem": 1, "texto": "O estagiário tem direito a recesso remunerado."},
        }

    # Consulta

    def buscar_trechos(self, consulta, limite=6):
        return self.trechos

    def salvar_pergunta(self, texto, resposta, encontrou, trechos_ids):
        pergunta_id = f"p{len(self.perguntas) + 1}"
        self.perguntas[pergunta_id] = {
            "id": pergunta_id,
            "texto": texto,
            "resposta": resposta,
            "encontrou": encontrou,
            "trechos_ids": trechos_ids,
        }
        return pergunta_id

    def obter_pergunta(self, pergunta_id):
        return self.perguntas.get(pergunta_id)

    def obter_trechos(self, ids):
        return [t for t in TRECHOS if t["id"] in ids]

    def criar_solicitacao(self, pergunta_id, telefone):
        solicitacao_id = f"s{len(self.solicitacoes) + 1}"
        self.solicitacoes[solicitacao_id] = {"id": solicitacao_id, "telefone": telefone, "status": "pendente"}
        return solicitacao_id

    def obter_solicitacao(self, solicitacao_id):
        return self.solicitacoes.get(solicitacao_id)

    def concluir_solicitacao(self, solicitacao_id, materiais):
        self.solicitacoes[solicitacao_id].update(status="enviado", materiais=materiais)

    def registrar_erro_solicitacao(self, solicitacao_id, erro):
        self.solicitacoes[solicitacao_id].update(status="erro", erro=erro)

    # Usuários e sessões

    def criar_usuario(self, nome, email, senha_hash, perfil):
        if self.obter_usuario_por_email(email):
            raise RegistroDuplicado("Já existe um usuário com este e-mail.")
        usuario = {
            "id": str(uuid.uuid4()),
            "nome": nome,
            "email": email.lower(),
            "senha_hash": senha_hash,
            "perfil": perfil,
            "ativo": True,
            "criado_em": datetime.now(timezone.utc).isoformat(),
        }
        self.usuarios[usuario["id"]] = usuario
        return publico(usuario)

    def obter_usuario_por_email(self, email):
        return next((u for u in self.usuarios.values() if u["email"] == email.lower()), None)

    def obter_usuario(self, usuario_id):
        usuario = self.usuarios.get(usuario_id)
        return publico(usuario) if usuario else None

    def listar_usuarios(self):
        return [publico(u) for u in self.usuarios.values()]

    def contar_administradores_ativos(self):
        return sum(1 for u in self.usuarios.values() if u["perfil"] == "administrador" and u["ativo"])

    def atualizar_usuario(self, usuario_id, campos):
        email = campos.get("email")
        dono = self.obter_usuario_por_email(email) if email else None
        if dono and dono["id"] != usuario_id:
            raise RegistroDuplicado("Já existe um usuário com este e-mail.")
        self.usuarios[usuario_id].update(campos)
        return publico(self.usuarios[usuario_id])

    def excluir_usuario(self, usuario_id):
        return self.usuarios.pop(usuario_id, None) is not None

    def criar_sessao(self, token_hash, usuario_id, expira_em):
        self.sessoes[token_hash] = {"usuario_id": usuario_id, "expira_em": expira_em.isoformat()}

    def obter_sessao(self, token_hash):
        sessao = self.sessoes.get(token_hash)
        if not sessao or sessao["usuario_id"] not in self.usuarios:
            return None
        return {"expira_em": sessao["expira_em"], "usuario": publico(self.usuarios[sessao["usuario_id"]])}

    def excluir_sessao(self, token_hash):
        self.sessoes.pop(token_hash, None)

    def excluir_sessoes_do_usuario(self, usuario_id):
        self.sessoes = {k: s for k, s in self.sessoes.items() if s["usuario_id"] != usuario_id}

    # Base de conhecimento

    def listar_temas(self):
        return TEMAS

    def _completar(self, trecho):
        tema = next(t for t in TEMAS if t["id"] == trecho["tema_id"])
        return {**trecho, "tema": tema["nome"], "url": tema["url"]}

    def listar_trechos(self, tema_id=None, busca=None, pagina=1, por_pagina=20):
        itens = [
            self._completar(t)
            for t in self.base.values()
            if (not tema_id or t["tema_id"] == tema_id)
            and (not busca or busca.lower() in (t["secao"] + t["texto"]).lower())
        ]
        inicio = (pagina - 1) * por_pagina
        return itens[inicio : inicio + por_pagina], len(itens)

    def obter_trecho(self, trecho_id):
        trecho = self.base.get(trecho_id)
        return self._completar(trecho) if trecho else None

    def criar_trecho(self, tema_id, secao, texto, usuario_id):
        trecho_id = max(self.base, default=0) + 1
        ordem = 1 + max((t["ordem"] for t in self.base.values() if t["tema_id"] == tema_id), default=0)
        self.base[trecho_id] = {"id": trecho_id, "tema_id": tema_id, "secao": secao, "ordem": ordem, "texto": texto}
        return self.obter_trecho(trecho_id)

    def atualizar_trecho(self, trecho_id, tema_id, secao, texto, usuario_id):
        if trecho_id not in self.base:
            return None
        self.base[trecho_id].update(tema_id=tema_id, secao=secao, texto=texto)
        return self.obter_trecho(trecho_id)

    def excluir_trecho(self, trecho_id):
        return self.base.pop(trecho_id, None) is not None

    def listar_perguntas(self, limite=50):
        return [
            {"id": p["id"], "texto": p["texto"], "encontrou": p["encontrou"], "criado_em": "2026-10-31T12:00:00+00:00"}
            for p in self.perguntas.values()
        ]

    # Inscrições

    def listar_inscricoes(self, usuario_id):
        return [i for i in self.inscricoes.values() if i["usuario_id"] == usuario_id]

    def criar_inscricao(self, usuario_id, tema_id, telefone):
        if any(i["tema_id"] == tema_id and i["telefone"] == telefone for i in self.inscricoes.values()):
            raise RegistroDuplicado("Você já acompanha este tema com este telefone.")
        tema = next(t for t in TEMAS if t["id"] == tema_id)
        inscricao = {
            "id": str(uuid.uuid4()),
            "usuario_id": usuario_id,
            "tema_id": tema_id,
            "tema": tema["nome"],
            "telefone": telefone,
        }
        self.inscricoes[inscricao["id"]] = inscricao
        return inscricao

    def excluir_inscricao(self, usuario_id, inscricao_id):
        inscricao = self.inscricoes.get(inscricao_id)
        if not inscricao or inscricao["usuario_id"] != usuario_id:
            return False
        del self.inscricoes[inscricao_id]
        return True


class IAFalsa:
    def __init__(self):
        self.resultado = {"encontrou": True, "resposta": "Você tem direito a 30 dias.", "trechos_usados": [10, 99]}
        self.recusar = False
        self.materiais = {
            "sites": [{"titulo": "Férias - gov.br", "url": "https://www.gov.br/ferias"}],
            "videos": [{"titulo": "Entenda suas férias", "url": "https://www.youtube.com/watch?v=abc"}],
        }
        self.falhar_materiais = False

    def responder(self, pergunta, trechos):
        if self.recusar:
            raise RecusaDaIA("recusada")
        return self.resultado

    def buscar_materiais(self, pergunta, tema):
        if self.falhar_materiais:
            raise RuntimeError("pesquisa indisponível")
        self.tema_pesquisado = tema
        return self.materiais


class WhatsAppFalso:
    def __init__(self):
        self.enviadas = []

    def enviar(self, telefone, texto):
        self.enviadas.append((telefone, texto))


@pytest.fixture
def falsos():
    repositorio, ia, whatsapp = RepositorioFalso(), IAFalsa(), WhatsAppFalso()
    app.dependency_overrides[obter_repositorio] = lambda: repositorio
    app.dependency_overrides[obter_ia] = lambda: ia
    app.dependency_overrides[obter_whatsapp] = lambda: whatsapp
    app.dependency_overrides[obter_configuracao] = lambda: Configuracao(
        supabase_url="https://exemplo.supabase.co",
        supabase_chave_servico="chave",
        twilio_account_sid="sid",
        twilio_auth_token="token",
        twilio_whatsapp_numero="+14155238886",
        twilio_sandbox_codigo="join teste-oraculo",
    )
    yield repositorio, ia, whatsapp
    app.dependency_overrides.clear()


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def entrar(client, falsos):
    """Cria um usuário com o perfil informado e devolve o cabeçalho de autenticação."""
    repositorio = falsos[0]

    def _entrar(perfil="administrador", email=None, senha="senha-segura-123"):
        email = email or f"{perfil}-{uuid.uuid4().hex[:6]}@oraculo.com.br"
        repositorio.criar_usuario(perfil.title(), email, gerar_hash_senha(senha), perfil)
        token = client.post("/api/auth/login", json={"email": email, "senha": senha}).json()["token"]
        return {"Authorization": f"Bearer {token}"}

    return _entrar


def expirar_sessoes(repositorio):
    passado = (datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat()
    for sessao in repositorio.sessoes.values():
        sessao["expira_em"] = passado
