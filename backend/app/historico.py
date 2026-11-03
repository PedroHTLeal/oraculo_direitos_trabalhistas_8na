"""Histórico de operações (Sprint 07): quem fez o quê e quando."""

import logging

logger = logging.getLogger(__name__)

# Ações registradas, com o nome exibido nos relatórios
ACOES = {
    "login": "Login",
    "cadastro": "Cadastro",
    "criar": "Inclusão",
    "alterar": "Alteração",
    "excluir": "Exclusão",
    "publicar": "Publicação",
    "reenviar": "Reenvio",
    "pedir_conteudo": "Pedido de conteúdo por e-mail",
}

ENTIDADES = {
    "conta": "Conta",
    "trecho": "Base de conhecimento",
    "usuario": "Usuários",
    "atualizacao": "Atualizações",
    "inscricao": "Temas acompanhados",
    "pergunta": "Consulta",
}


def registrar(repositorio, usuario, acao, entidade, entidade_id, descricao):
    """Grava a operação; uma falha aqui nunca impede a operação principal."""
    try:
        repositorio.registrar_operacao(usuario, acao, entidade, entidade_id, descricao)
    except Exception:
        logger.exception("Não foi possível registrar a operação %s/%s no histórico", acao, entidade)
