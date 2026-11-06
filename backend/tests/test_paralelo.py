import threading
import time

from app.paralelo import executar_em_paralelo
from tests.test_atualizacoes import NOVA, inscrever


def test_resultados_voltam_na_ordem_das_tarefas():
    tarefas = [lambda n=n: (time.sleep(0.05 * (3 - n)), n)[1] for n in range(3)]
    assert executar_em_paralelo(tarefas) == [0, 1, 2]
    assert executar_em_paralelo([]) == []


def test_tarefas_rodam_ao_mesmo_tempo():
    # A barreira só libera quando as 3 tarefas estão rodando juntas; em sequência, daria erro de tempo
    barreira = threading.Barrier(3, timeout=5)
    assert executar_em_paralelo([barreira.wait for _ in range(3)]) is not None


def test_novidade_e_enviada_aos_inscritos_em_paralelo(client, falsos, entrar):
    repositorio, _, email = falsos
    for numero in range(3):
        inscrever(client, entrar, 1, f"pessoa{numero}@exemplo.com.br")
    barreira = threading.Barrier(3, timeout=5)
    enviar_original = email.enviar

    def enviar_junto(destinatario, conteudo):
        barreira.wait()  # trava se os e-mails forem enviados um de cada vez
        enviar_original(destinatario, conteudo)

    email.enviar = enviar_junto
    client.post("/api/atualizacoes", json=NOVA, headers=entrar("curador"))

    assert len(email.enviados) == 3
    assert {e["status"] for e in repositorio.envios} == {"enviado"}
