"""Execução em paralelo de tarefas independentes.

As tarefas do Oráculo passam a maior parte do tempo esperando a rede (banco de
dados, Gmail). Com várias threads, essas esperas acontecem ao mesmo tempo, e o
tempo total fica próximo ao da tarefa mais lenta, em vez da soma de todas.
"""

from concurrent.futures import ThreadPoolExecutor

LIMITE_PADRAO = 6


def executar_em_paralelo(funcoes, limite=LIMITE_PADRAO):
    """Roda as funções (sem argumentos) ao mesmo tempo e devolve os resultados na mesma ordem."""
    if not funcoes:
        return []
    with ThreadPoolExecutor(max_workers=min(limite, len(funcoes))) as executor:
        return [futuro.result() for futuro in [executor.submit(funcao) for funcao in funcoes]]
