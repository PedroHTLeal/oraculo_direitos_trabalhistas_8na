"""Textos da documentação da API (Swagger em /api/docs e docs/api.md).

Cada rota tem um resumo, uma descrição e quem pode usá-la. Um teste garante que
toda rota nova entre aqui, para a documentação nunca ficar desatualizada.
"""

DESCRICAO = """API do **Oráculo dos Direitos Trabalhistas**: consulta à Cartilha de Direitos e Obrigações
no Trabalho do TRT4 com IA (RAG), envio de conteúdo complementar por e-mail, acompanhamento
de temas e painel da equipe.

**Autenticação:** as rotas restritas usam o token devolvido por `POST /api/auth/login`, enviado no
cabeçalho `Authorization: Bearer <token>`. A sessão vale por 8 horas.

**Erros:** todas as respostas de erro trazem `detail` com uma frase pronta para mostrar ao usuário;
os erros de validação (422) trazem também `erros`, uma mensagem por campo."""

TEMAS = [
    {"name": "Consulta", "description": "Perguntas sobre direitos trabalhistas e o \"Saber mais\" por e-mail. Abertas, sem login."},
    {"name": "Autenticação", "description": "Cadastro, login e logout."},
    {"name": "Usuários", "description": "Gestão de contas e perfis. Só administradores."},
    {"name": "Base de conhecimento", "description": "Trechos da cartilha usados pela IA e auditoria das perguntas."},
    {"name": "Conteúdo complementar", "description": "Sinônimos da busca e sites e vídeos enviados no \"Saber mais\"."},
    {"name": "Acompanhamento de temas", "description": "Temas que cada usuário acompanha."},
    {"name": "Atualizações", "description": "Novidades dos temas, enviadas por e-mail a quem acompanha."},
    {"name": "Dashboard e relatórios", "description": "Indicadores, relatórios com filtros, exportação em CSV e histórico."},
]

ABERTA = "Aberta (sem login)"
LOGADO = "Qualquer pessoa logada"
EQUIPE = "Curador ou administrador"
ADMIN = "Administrador"

# (método, rota): (resumo, descrição, acesso)
ROTAS = {
    ("GET", "/api/saude"): ("Situação do serviço", "Confere se a API está no ar.", ABERTA),
    ("GET", "/api/sugestoes"): ("Temas e perguntas sugeridos", "Perguntas exibidas na página inicial (RF02).", ABERTA),
    ("POST", "/api/perguntas"): (
        "Fazer uma pergunta",
        "Busca os trechos da cartilha mais relevantes e gera a resposta com a IA usando só esses trechos (RAG). "
        "Devolve a resposta, as fontes e se a cartilha trata do assunto (RF04 a RF09).",
        ABERTA,
    ),
    ("POST", "/api/saiba-mais"): (
        "Pedir mais conteúdo por e-mail",
        "Envia ao e-mail informado a resposta, sites e vídeos sobre o assunto. Exige a autorização (LGPD); "
        "até 5 pedidos por e-mail a cada hora (RF10, RF11).",
        ABERTA,
    ),
    ("GET", "/api/saiba-mais/{solicitacao_id}"): ("Situação do pedido de e-mail", "pendente, enviado ou erro.", ABERTA),
    ("POST", "/api/auth/cadastro"): ("Criar conta", "Cria uma conta de usuário comum e já abre a sessão.", ABERTA),
    ("POST", "/api/auth/login"): ("Entrar", "Devolve o token de acesso e os dados da conta.", ABERTA),
    ("POST", "/api/auth/sair"): ("Sair", "Encerra a sessão do token enviado.", LOGADO),
    ("GET", "/api/auth/eu"): ("Conta atual", "Dados da pessoa dona do token.", LOGADO),
    ("GET", "/api/usuarios"): ("Listar usuários", "Todas as contas, com perfil e situação.", ADMIN),
    ("POST", "/api/usuarios"): ("Cadastrar usuário", "Cria uma conta com o perfil escolhido.", ADMIN),
    ("PUT", "/api/usuarios/{usuario_id}"): (
        "Alterar usuário",
        "Altera nome, e-mail, perfil, situação ou senha. O sistema nunca fica sem um administrador ativo.",
        ADMIN,
    ),
    ("DELETE", "/api/usuarios/{usuario_id}"): ("Excluir usuário", "Ninguém pode excluir a própria conta.", ADMIN),
    ("GET", "/api/temas"): ("Listar temas da cartilha", "As 25 páginas da cartilha do TRT4.", ABERTA),
    ("GET", "/api/base/trechos"): ("Listar trechos", "Com filtro por tema, busca no texto e paginação.", EQUIPE),
    ("GET", "/api/base/trechos/{trecho_id}"): ("Ver trecho", "Um trecho da cartilha.", EQUIPE),
    ("POST", "/api/base/trechos"): ("Incluir trecho", "Novo trecho, já usado pela IA nas respostas (UC07).", EQUIPE),
    ("PUT", "/api/base/trechos/{trecho_id}"): ("Alterar trecho", "Altera tema, subtítulo ou texto.", EQUIPE),
    ("DELETE", "/api/base/trechos/{trecho_id}"): ("Excluir trecho", "Remove o trecho da base.", EQUIPE),
    ("GET", "/api/sinonimos"): ("Listar sinônimos", "Palavras do dia a dia e os termos da cartilha que a busca usa no lugar.", EQUIPE),
    ("POST", "/api/sinonimos"): ("Incluir sinônimo", "Grava sem acentos e em minúsculas.", EQUIPE),
    ("PUT", "/api/sinonimos/{termo}"): ("Alterar sinônimo", "Altera a palavra ou os termos equivalentes.", EQUIPE),
    ("DELETE", "/api/sinonimos/{termo}"): ("Excluir sinônimo", "A busca deixa de traduzir a palavra.", EQUIPE),
    ("GET", "/api/materiais"): ("Listar sites e vídeos", "Links do \"Saber mais\", por assunto.", EQUIPE),
    ("POST", "/api/materiais"): ("Incluir site ou vídeo", "Vídeos só do YouTube; o mesmo link não se repete no assunto.", EQUIPE),
    ("PUT", "/api/materiais/{material_id}"): ("Alterar site ou vídeo", "Altera os dados do link.", EQUIPE),
    ("DELETE", "/api/materiais/{material_id}"): ("Excluir site ou vídeo", "O link deixa de ser enviado.", EQUIPE),
    ("GET", "/api/inscricoes"): ("Meus temas", "Temas que a pessoa logada acompanha.", LOGADO),
    ("POST", "/api/inscricoes"): ("Acompanhar tema", "As novidades do tema passam a chegar no e-mail da conta (RF12).", LOGADO),
    ("DELETE", "/api/inscricoes/{inscricao_id}"): ("Deixar de acompanhar", "Só as inscrições da própria conta.", LOGADO),
    ("GET", "/api/atualizacoes"): ("Listar atualizações", "Novidades publicadas, com a situação dos envios.", EQUIPE),
    ("POST", "/api/atualizacoes"): (
        "Publicar novidade",
        "Salva a novidade e envia por e-mail, em paralelo, a quem acompanha o tema (RF13).",
        EQUIPE,
    ),
    ("POST", "/api/atualizacoes/{atualizacao_id}/reenviar"): ("Reenviar falhas", "Envia de novo só os e-mails que deram erro.", EQUIPE),
    ("DELETE", "/api/atualizacoes/{atualizacao_id}"): (
        "Excluir atualização",
        "O curador só exclui as próprias publicações; o administrador, qualquer uma.",
        EQUIPE,
    ),
    ("GET", "/api/minhas-atualizacoes"): ("Novidades dos meus temas", "Últimas novidades dos temas acompanhados.", LOGADO),
    ("GET", "/api/painel/indicadores"): ("Indicadores do dashboard", "Período de 7, 30, 90 ou 365 dias.", EQUIPE),
    ("GET", "/api/relatorios/perguntas"): (
        "Relatório de perguntas",
        "Auditoria das perguntas, sem dados pessoais (UC08): filtros por período, tema, resultado e texto; `formato=csv` exporta.",
        EQUIPE,
    ),
    ("GET", "/api/relatorios/historico"): (
        "Histórico de operações",
        "Quem fez o quê e quando; filtros por período, ação, área e texto; `formato=csv` exporta.",
        ADMIN,
    ),
}


def aplicar(app):
    """Coloca o resumo e a descrição de cada rota no Swagger."""
    for rota in app.routes:
        for metodo in getattr(rota, "methods", None) or ():
            texto = ROTAS.get((metodo, rota.path))
            if texto:
                resumo, descricao, acesso = texto
                rota.summary = resumo
                rota.description = f"{descricao}\n\n**Acesso:** {acesso}."
