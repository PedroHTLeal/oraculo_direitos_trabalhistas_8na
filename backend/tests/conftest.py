import uuid
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

from app.config import Configuracao
from app.dependencias import obter_configuracao, obter_ia, obter_repositorio, obter_whatsapp
from app.ia import RecusaDaIA
from app.main import app
from app.rotas.atualizacoes import whatsapp_opcional
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
        self.atualizacoes = {}
        self.envios = []
        self.historico = []
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

    def criar_solicitacao(self, pergunta_id, telefone, usuario_id=None):
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

    def criar_usuario(self, nome, email, telefone, senha_hash, perfil, consentimento_whatsapp=False):
        if email and self.obter_usuario_por_email(email):
            raise RegistroDuplicado("Já existe um usuário com este e-mail.")
        if telefone and self.obter_usuario_por_telefone(telefone):
            raise RegistroDuplicado("Já existe uma conta com este telefone.")
        usuario = {
            "id": str(uuid.uuid4()),
            "nome": nome,
            "email": email.lower() if email else None,
            "telefone": telefone,
            "senha_hash": senha_hash,
            "perfil": perfil,
            "ativo": True,
            "criado_em": datetime.now(timezone.utc).isoformat(),
        }
        self.usuarios[usuario["id"]] = usuario
        return publico(usuario)

    def obter_usuario_por_email(self, email):
        return next((u for u in self.usuarios.values() if u["email"] == email.lower()), None)

    def obter_usuario_por_telefone(self, telefone):
        return next((u for u in self.usuarios.values() if u["telefone"] == telefone), None)

    def obter_usuario(self, usuario_id):
        usuario = self.usuarios.get(usuario_id)
        return publico(usuario) if usuario else None

    def listar_usuarios(self):
        return [publico(u) for u in self.usuarios.values()]

    def contar_administradores_ativos(self):
        return sum(1 for u in self.usuarios.values() if u["perfil"] == "administrador" and u["ativo"])

    def atualizar_usuario(self, usuario_id, campos):
        email, telefone = campos.get("email"), campos.get("telefone")
        dono = self.obter_usuario_por_email(email) if email else None
        if dono and dono["id"] != usuario_id:
            raise RegistroDuplicado("Já existe um usuário com este e-mail.")
        dono = self.obter_usuario_por_telefone(telefone) if telefone else None
        if dono and dono["id"] != usuario_id:
            raise RegistroDuplicado("Já existe uma conta com este telefone.")
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


    # Atualizações (Módulo 2)

    def criar_atualizacao(self, tema_id, titulo, conteudo, url, autor_id):
        atualizacao_id = len(self.atualizacoes) + 1
        self.atualizacoes[atualizacao_id] = {
            "id": atualizacao_id,
            "tema_id": tema_id,
            "titulo": titulo,
            "conteudo": conteudo,
            "url": url,
            "autor_id": autor_id,
            "publicado_em": datetime.now(timezone.utc).isoformat(),
        }
        return self.obter_atualizacao(atualizacao_id)

    def _completar_atualizacao(self, a):
        envios = [e for e in self.envios if e["atualizacao_id"] == a["id"]]
        autor = self.usuarios.get(a["autor_id"])
        return {
            **a,
            "tema": next(t["nome"] for t in TEMAS if t["id"] == a["tema_id"]),
            "autor": autor["nome"] if autor else None,
            "envios": {s: sum(1 for e in envios if e["status"] == s) for s in ("pendente", "enviado", "erro")},
        }

    def listar_atualizacoes(self, tema_id=None):
        return [self._completar_atualizacao(a) for a in self.atualizacoes.values() if not tema_id or a["tema_id"] == tema_id]

    def obter_atualizacao(self, atualizacao_id):
        a = self.atualizacoes.get(atualizacao_id)
        return self._completar_atualizacao(a) if a else None

    def excluir_atualizacao(self, atualizacao_id):
        return self.atualizacoes.pop(atualizacao_id, None) is not None

    def listar_inscricoes_ativas(self, tema_id):
        return [{"id": i["id"], "telefone": i["telefone"]} for i in self.inscricoes.values() if i["tema_id"] == tema_id]

    def criar_envios(self, atualizacao_id, inscricoes_ids):
        self.envios += [{"atualizacao_id": atualizacao_id, "inscricao_id": i, "status": "pendente"} for i in inscricoes_ids]

    def listar_envios(self, atualizacao_id, status=None):
        telefones = {i["id"]: i["telefone"] for i in self.inscricoes.values()}
        return [
            {"inscricao_id": e["inscricao_id"], "status": e["status"], "telefone": telefones[e["inscricao_id"]]}
            for e in self.envios
            if e["atualizacao_id"] == atualizacao_id and (not status or e["status"] == status)
        ]

    def registrar_envio(self, atualizacao_id, inscricao_id, status):
        for e in self.envios:
            if e["atualizacao_id"] == atualizacao_id and e["inscricao_id"] == inscricao_id:
                e["status"] = status

    def atualizacoes_do_usuario(self, usuario_id, limite=20):
        temas = {i["tema_id"] for i in self.listar_inscricoes(usuario_id)}
        return [a for a in self.listar_atualizacoes() if a["tema_id"] in temas][:limite]

    # Histórico, dashboard e relatórios

    def registrar_operacao(self, usuario, acao, entidade, entidade_id, descricao):
        self.historico.append(
            {
                "id": len(self.historico) + 1,
                "usuario_id": usuario["id"] if usuario else None,
                "usuario_nome": usuario["nome"] if usuario else None,
                "acao": acao,
                "entidade": entidade,
                "entidade_id": str(entidade_id),
                "descricao": descricao,
                "criado_em": datetime.now(timezone.utc).isoformat(),
            }
        )

    def listar_historico(self, inicio=None, fim=None, acao=None, entidade=None, busca=None, limite=500):
        return [
            h
            for h in reversed(self.historico)
            if (not acao or h["acao"] == acao)
            and (not entidade or h["entidade"] == entidade)
            and (not busca or busca.lower() in (h["descricao"] + (h["usuario_nome"] or "")).lower())
            and (not inicio or h["criado_em"] >= inicio)
            and (not fim or h["criado_em"] < fim)
        ][:limite]

    def perguntas_no_periodo(self, inicio=None, fim=None, encontrou=None, busca=None, tema_id=None, limite=1000):
        resultado = []
        for p in self.perguntas.values():
            criado_em = p.get("criado_em") or datetime.now(timezone.utc).isoformat()
            temas = sorted({t["tema"] for t in TRECHOS if t["id"] in p["trechos_ids"]})
            if inicio and criado_em < inicio or fim and criado_em >= fim:
                continue
            if encontrou is not None and p["encontrou"] != encontrou:
                continue
            if busca and busca.lower() not in p["texto"].lower():
                continue
            if tema_id and next(t["nome"] for t in TEMAS if t["id"] == tema_id) not in temas:
                continue
            resultado.append({"id": p["id"], "texto": p["texto"], "encontrou": p["encontrou"], "criado_em": criado_em, "temas": temas})
        return resultado

    def solicitacoes_no_periodo(self, inicio=None, fim=None):
        return [{"status": s["status"], "criado_em": datetime.now(timezone.utc).isoformat()} for s in self.solicitacoes.values()]

    def resumo_inscricoes(self):
        return [{"tema_id": i["tema_id"], "temas": {"nome": i["tema"]}} for i in self.inscricoes.values()]


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
    app.dependency_overrides[whatsapp_opcional] = lambda: whatsapp
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

    def _entrar(perfil="administrador", login=None, senha="senha-segura-123"):
        # A equipe entra com e-mail; o usuário comum, com o telefone
        if perfil == "usuario":
            login = login or f"+55119{uuid.uuid4().int % 10**8:08d}"
            repositorio.criar_usuario("Usuário", None, login, gerar_hash_senha(senha), perfil, True)
        else:
            login = login or f"{perfil}-{uuid.uuid4().hex[:6]}@oraculo.com.br"
            repositorio.criar_usuario(perfil.title(), login, None, gerar_hash_senha(senha), perfil)
        token = client.post("/api/auth/login", json={"identificador": login, "senha": senha}).json()["token"]
        return {"Authorization": f"Bearer {token}"}

    return _entrar


def expirar_sessoes(repositorio):
    passado = (datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat()
    for sessao in repositorio.sessoes.values():
        sessao["expira_em"] = passado
