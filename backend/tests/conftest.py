import pytest
from fastapi.testclient import TestClient

from app.config import Configuracao
from app.ia import RecusaDaIA
from app.main import app, obter_configuracao, obter_ia, obter_repositorio, obter_whatsapp

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


class RepositorioFalso:
    def __init__(self):
        self.trechos = list(TRECHOS)
        self.perguntas = {}
        self.solicitacoes = {}

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
