# Sprint 09 — Verificação completa e documentação

**Situação:** Concluída: testes com o banco real, a IA (Gemini) e o envio de e-mail reais; prints refeitos em 03/11/2026 · [← Voltar ao índice](../../README.md)

## O que a Sprint pediu

Testes funcionais, correção de bugs, testes de validação, testes de navegação e atualização da documentação técnica.

## Como os testes foram feitos

| Tipo | Ferramenta | Resultado |
| --- | --- | --- |
| **Automatizados (backend)** | 88 testes com `pytest` (rodar `pytest` em `backend/`), com versões simuladas do banco, da IA e do e-mail | 88 de 88 passando |
| **Funcionais, de validação e de navegação** | Roteiro [`capturar_evidencias.py`](../../ferramentas/capturar_evidencias.py), que usa o navegador Edge, o sistema rodando localmente e o **banco real** no Supabase. Cada passo verifica o que deve aparecer na tela e salva um print | 35 de 35 passos aprovados (03/11/2026) |
| **Integração contínua** | [GitHub Actions](../../../.github/workflows/testes.yml): a cada envio ao GitHub, roda os testes do backend e confere e compila o frontend | Automático a cada envio |
| **Avaliação das respostas da IA** | [`avaliar_respostas.py`](../../ferramentas/avaliar_respostas.py): 15 perguntas de referência com a IA real | Ver [avaliação](../../avaliacao-ia.md) |
| **Persistência** | O roteiro roda em duas fases; entre elas o sistema é encerrado e aberto de novo | Dados mantidos |

## Casos de teste (sistema real, 02 e 03/11/2026)

| # | Caso de teste | Perfil | Resultado esperado | Resultado obtido | Evidência |
| --- | --- | --- | --- | --- | --- |
| CT01 | Entrar sem preencher os campos | Visitante | Mensagem "Preencha o campo e-mail." | Conforme esperado | [print](../../evidencias/02-login-validacao.png) |
| CT02 | Entrar com senha errada | Visitante | Mensagem genérica, sem revelar se a conta existe | Conforme esperado | [print](../../evidencias/03-login-senha-errada.png) |
| CT03 | Cadastro com nome curto, e-mail e senha inválidos e senhas diferentes | Visitante | Uma mensagem junto de cada campo | Conforme esperado | [print](../../evidencias/04-cadastro-validacao.png) |
| CT04 | Cadastro com e-mail já usado | Visitante | "Já existe um usuário com este e-mail." | Conforme esperado | [print](../../evidencias/05-cadastro-email-repetido.png) |
| CT05 | Cadastro válido | Visitante | Conta criada e pessoa levada a "Meus temas" | Conforme esperado | [print](../../evidencias/06-cadastro-sucesso.png) |
| CT06 | Acompanhar tema sem escolher o tema | Usuário | "Preencha o campo tema." | Conforme esperado | [print](../../evidencias/07-temas-validacao.png) |
| CT07 | Acompanhar o tema Férias | Usuário | Confirmação e tema na lista | Conforme esperado | [print](../../evidencias/08-temas-inscricao.png) |
| CT08 | Abrir a base de conhecimento pelo endereço | Usuário | "Acesso não permitido" | Conforme esperado | [print](../../evidencias/09-usuario-sem-acesso.png) |
| CT09 | Entrar como curador | Curador | Abre o Dashboard com dados reais | Conforme esperado (após a correção do bug B06) | [print](../../evidencias/10-dashboard.png) |
| CT10 | Filtrar a base por tema e pesquisar "recesso" | Curador | Só trechos do tema com o termo | Conforme esperado | [print](../../evidencias/12-base-filtro.png) |
| CT11 | Salvar trecho sem campos | Curador | "Preencha o campo tema." e demais campos | Conforme esperado | [print](../../evidencias/13-trecho-validacao.png) |
| CT12 | Cadastrar, editar e salvar um trecho | Curador | Mensagens "Trecho cadastrado." e "Trecho atualizado." | Conforme esperado | [print](../../evidencias/16-trecho-atualizado.png) |
| CT13 | Publicar atualização sem título | Curador | "Preencha o campo título." | Conforme esperado | [print](../../evidencias/17-atualizacao-validacao.png) |
| CT14 | Publicar atualização do tema Férias sem o e-mail configurado | Curador | Publicação salva; envio marcado com erro e botão "Reenviar" | Conforme esperado | [print](../../evidencias/18-atualizacao-publicada.png) |
| CT15 | Abrir o histórico de operações | Curador | "Acesso não permitido" (exclusivo do administrador) | Conforme esperado | [print](../../evidencias/19-curador-sem-acesso-historico.png) |
| CT16 | Fechar e abrir o sistema e procurar o trecho cadastrado | Curador | Trecho continua salvo | Conforme esperado | [print](../../evidencias/20-persistencia-apos-reiniciar.png) |
| CT17 | Excluir o trecho | Curador | Confirmação e depois "Trecho excluído." | Conforme esperado | [print](../../evidencias/22-trecho-excluido.png) |
| CT18 | Exportar o relatório de perguntas | Curador | Arquivo CSV baixado | Conforme esperado | [CSV](../../evidencias/relatorio-perguntas.csv) |
| CT19 | Ver as novidades do tema acompanhado | Usuário | A atualização publicada aparece em "Meus temas" | Conforme esperado | [print](../../evidencias/24-usuario-novidades.png) |
| CT20 | Salvar novo usuário sem dados | Administrador | "Preencha o campo nome." | Conforme esperado | [print](../../evidencias/26-usuario-validacao.png) |
| CT21 | Rebaixar o próprio perfil de administrador | Administrador | Bloqueado com explicação | Conforme esperado | [print](../../evidencias/27-regra-administrador.png) |
| CT22 | Excluir o usuário cadastrado no CT05 | Administrador | Confirmação e "Usuário excluído." | Conforme esperado | [print](../../evidencias/29-usuario-excluido.png) |
| CT23 | Filtrar o histórico pela ação "Exclusão" e exportar | Administrador | Só exclusões, com quem fez e quando; CSV baixado | Conforme esperado | [print](../../evidencias/31-historico-filtro-exclusao.png) · [CSV](../../evidencias/historico-de-operacoes.csv) |
| CT24 | Consulta, cadastro e painel no celular | Todos | Telas adaptadas, sem rolagem lateral | Conforme esperado | [print](../../evidencias/35-celular-painel.png) |
| CT25 | Perguntar "Quantos dias de férias eu tenho direito?" com a IA real | Visitante | Resposta da cartilha em cerca de 15 s, com fontes e o convite "Quer saber mais?" | Conforme esperado (03/11/2026) | — |
| CT26 | "Saber mais" com nome e e-mail reais | Visitante | E-mail recebido com a resposta, 2 sites (Jusbrasil e cartilha do TRT4) e 2 vídeos (CEISC e Contas Online); pedido marcado como "enviado" no banco | Conforme esperado (03/11/2026) | — |
| CT27 | Perguntar "Qual é a capital da França?" e uma pergunta sobre imposto de renda de empresas no exterior | Visitante | Aviso de que a cartilha não trata do assunto, sem fontes e sem o convite "Quer saber mais?" (RF09) | Conforme esperado (04/11/2026) | — |

## Bugs encontrados e corrigidos

| # | Bug | Como foi encontrado | Correção |
| --- | --- | --- | --- |
| B01 | A busca não encontrava "estágio" nem com a palavra exata | Teste com o banco real | Função de busca corrigida ([SQL 002](../../../supabase/002_corrige_busca_e_sinonimos.sql)) |
| B02 | "Demitido", "patrão" e "FGTS" não encontravam os temas certos | Teste com o banco real | Tabela de sinônimos |
| B03 | Erro 500 intermitente ao abrir a base | Roteiro de navegação | Repetição automática quando a conexão cai ([`4165443`](https://github.com/PedroHTLeal/oraculo_direitos_trabalhistas_8na/commit/4165443)) |
| B04 | Filtro de período do dashboard sempre recusado | Testes automatizados | Validação própria do período |
| B05 | A dica do gráfico cobria a legenda | Revisão dos prints | Dica posicionada sobre a barra ([`d916d51`](https://github.com/PedroHTLeal/oraculo_direitos_trabalhistas_8na/commit/d916d51)) |
| B06 | Depois de sair, a próxima pessoa que entrava era levada para a página da pessoa anterior | Roteiro de navegação | O endereço de retorno não é guardado quando a pessoa clica em Sair ([`ad724c3`](https://github.com/PedroHTLeal/oraculo_direitos_trabalhistas_8na/commit/ad724c3)) |

## Pendências e como serão resolvidas

| Pendência | Ação prevista |
| --- | --- |
| Mais assuntos com sites e vídeos escolhidos | A equipe envia os links das demais perguntas sugeridas |
