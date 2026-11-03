import os


def agendar(tarefas, funcao, *argumentos):
    """Roda a tarefa depois de responder ao navegador.

    Na Vercel a função para logo depois da resposta, então lá a tarefa roda
    dentro do próprio pedido (a Vercel define a variável VERCEL=1).
    """
    if os.getenv("VERCEL"):
        funcao(*argumentos)
    else:
        tarefas.add_task(funcao, *argumentos)
