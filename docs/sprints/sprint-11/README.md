# Sprint 11 — Preparação para entrega

**Situação:** Concluída · [← Voltar ao índice](../../README.md)

## O que a Sprint pediu

Organizar e finalizar a documentação e os materiais técnicos para a entrega: Manual do Usuário, Manual Técnico, documentação final consolidada, revisão completa do código e organização do GitHub.

## Entregas

| Item pedido | Entrega | Onde ver |
| --- | --- | --- |
| **Manual do Usuário** | Apresentação, público-alvo, acesso e perfis, passo a passo da consulta, do "Saber mais", da conta e de cada tela do painel, com 18 imagens das telas e do e-mail, e uma tabela de mensagens e situações comuns | [manual-do-usuario.md](../../manual-do-usuario.md) |
| **Manual Técnico** | Arquitetura, tecnologias e versões, organização dos módulos, banco, requisitos, instalação, execução, variáveis de ambiente (sem valores), APIs, componente de IA (RAG), regras de negócio, segurança, testes e manutenção | [manual-tecnico.md](../../manual-tecnico.md) |
| **Documentação final** | Revisada para refletir a versão atual (detalhes abaixo) | [Índice da documentação](../../README.md) |
| **Revisão do código** | Verificação automática, código sem uso removido, dependências e informações sensíveis conferidas (detalhes abaixo) | [Revisão do código](#revisão-do-código) |
| **Organização do GitHub** | Raiz do repositório organizada, arquivos desnecessários retirados, README e documentação atualizados | [Repositório](https://github.com/PedroHTLeal/oraculo_direitos_trabalhistas_8na) |

## Documentação final consolidada

| Assunto | Documento |
| --- | --- |
| Requisitos, casos de uso, backlog e cronograma (com a situação final de cada item) | [Relatório da Sprint 01](../sprint-01/relatorio.md) |
| Arquitetura, diagrama de classes, MER e modelo relacional | [Diagramas](../sprint-02/diagramas.md) |
| Banco de dados final | [banco-de-dados.md](../../banco-de-dados.md) |
| APIs | [api.md](../../api.md) e Swagger em https://oraculo-direitos-trabalhistas-8na.vercel.app/api/docs |
| Regras de negócio | [Manual Técnico, seção 10](../../manual-tecnico.md#10-regras-de-negócio) |
| Componente de IA e sua avaliação | [Manual Técnico, seção 9](../../manual-tecnico.md#9-componente-de-ia-rag) e [avaliacao-ia.md](../../avaliacao-ia.md) |
| Paralelismo | [paralelismo.md](../../paralelismo.md) |
| Decisões e mudanças de escopo | [decisoes.md](../../decisoes.md) |
| Histórico de versões | [CHANGELOG](../../../CHANGELOG.md) |

Ajustes de coerência feitos nesta revisão: a Sprint 08 foi encerrada (a revisão final das regras de negócio ficou no Manual Técnico); o índice passou a listar os manuais, os scripts `001` a `008` e o relatório com as Sprints 01 a 11; o README mostra os números atuais (111 testes, 38 rotas) e os links dos manuais.

## Revisão do código

| Verificação | O que foi encontrado | O que foi feito |
| --- | --- | --- |
| **Verificação automática do Python** (ruff: erros, armadilhas comuns e modernização) | 9 rotas transformavam um erro em resposta HTTP sem guardar a causa original; 1 import sem uso; 12 usos de uma forma antiga de indicar o fuso horário; 1 variável sem uso | Todos corrigidos; a configuração fica em [`ruff.toml`](../../../ruff.toml), e o ruff passou a rodar no GitHub Actions a cada envio |
| **Código sem uso** | A rota antiga `GET /api/base/perguntas`, substituída pelo relatório de perguntas (com filtros e exportação) e não usada pela interface | Rota, modelo, método do banco e teste removidos (a API passou de 39 para 38 rotas) |
| **Componentes da interface** | Todos os componentes e funções da API do frontend são usados; nenhum `console.log` ou código de depuração | — |
| **Dependências do frontend** (`npm audit`) | 3 falhas de gravidade alta no React Router (redirecionamento aberto) | Atualizado para a versão 6.30.6, que corrige as três. Restam 2 de gravidade moderada que exigem a versão 7: uma afeta só a renderização no servidor (não usada) e a outra, links montados com texto do usuário (o Oráculo só navega para endereços fixos) |
| **Informações sensíveis** | Nenhuma chave em uso aparece nos arquivos nem no histórico de commits (conferido comparando cada chave do `.env` com todo o histórico, sem exibi-las); o `.env` está no `.gitignore` e um teste impede valores no `.env.example` | Credenciais antigas de testes de 02/11, já fora de uso, aparecem em commits daquela data: recomenda-se revogá-las nos painéis dos serviços (próximos passos) |
| **Tratamento de erros** | Mensagens em português para validação, login, IA ocupada, banco fora do ar e falhas de envio; erros inesperados vão para o log com mensagem genérica ao usuário | Mantido; conferido nos testes |
| **Testes** | 111 testes automatizados, todos passando; ESLint sem avisos; compilação do frontend sem erros | — |

## Organização do GitHub

- **Raiz do repositório** só com o necessário para entender e executar o projeto: `README.md`, `CHANGELOG.md`, dependências (`requirements.txt`), configuração da publicação (`vercel.json`), da verificação (`ruff.toml`), scripts de execução (`iniciar.bat`, `iniciar.sh`) e as pastas `backend/`, `frontend/`, `supabase/`, `api/`, `docs/` e `.github/`.
- **Arquivos movidos ou retirados:** o PDF original da Sprint 01 saiu da raiz e foi para [`docs/sprints/sprint-01/`](../sprint-01/); a configuração local do assistente de desenvolvimento (`.claude/`) saiu do repositório; caches das ferramentas entraram no `.gitignore`.
- **Histórico de commits:** um commit por ajuste no `main`, todos com data, objetivo, o que foi feito e como agrega; versões marcadas com tags (`v1.0.0-rc.1` a `v1.0.0-rc.4`).
- **Integrantes e informações gerais:** no README e no relatório da Sprint 01.

## Principais correções e melhorias desde a Sprint 10

| Problema ou melhoria | O que foi feito |
| --- | --- |
| A IA falhava quando o modelo principal e o reserva estavam ocupados ao mesmo tempo | Fila de 3 modelos reserva, dentro do limite de 60 s da Vercel |
| O link de vídeos do e-mail abria a página inicial do YouTube no celular | Vídeos do YouTube sobre a pergunta: links diretos pela API do YouTube (com a chave) ou a pesquisa filtrada para só vídeos |
| A busca dava peso a palavras genéricas ("até", "sem", "ficar") | Palavras genéricas ignoradas na reordenação |
| O banco gratuito pausava depois de 7 dias sem uso | Rotina no GitHub Actions que usa o banco a cada 2 dias |
| Código sem uso, exceções sem causa original e falhas de segurança em dependências | Corrigidos na revisão do código |

## Ajustes desta Sprint

| Commit | O que mudou |
| --- | --- |
| [`72e616c`](https://github.com/PedroHTLeal/oraculo_direitos_trabalhistas_8na/commit/72e616c) | Rotina que mantém o banco ativo |
| [`6d9370b`](https://github.com/PedroHTLeal/oraculo_direitos_trabalhistas_8na/commit/6d9370b) | Fila de modelos reserva da IA |
| [`63dbabc`](https://github.com/PedroHTLeal/oraculo_direitos_trabalhistas_8na/commit/63dbabc) | Vídeos do YouTube sobre a pergunta no e-mail |
| [`f706f8c`](https://github.com/PedroHTLeal/oraculo_direitos_trabalhistas_8na/commit/f706f8c) | Busca ignora palavras genéricas |
| Commit da Sprint 11 | Manuais, revisão do código, organização do GitHub e relatório com as Sprints 01 a 11 |

## Pendências e próximos passos

| Pendência | Responsável e próximo passo |
| --- | --- |
| Chave da API do YouTube | **Gerson Martinho Mesquita Neto:** criar a chave e configurar no `backend/.env` e na Vercel ([guia, seção 4](../../configuracao.md)) |
| Conversa com o outro orientador sobre paralelismo | Equipe: apresentar o [material de paralelismo](../../paralelismo.md) e registrar as observações |
| Teste de usabilidade com pessoas do público-alvo | Equipe: testar com trabalhadores e estudantes antes da apresentação final, usando o Manual do Usuário |
| Revogar credenciais antigas de testes (02/11) | Equipe: apagar nos painéis da Meta e do Google as chaves usadas nos primeiros testes, que não estão mais em uso |
| Migrar o React Router para a versão 7 | Equipe: depois da apresentação, para eliminar os 2 alertas moderados restantes |
| Conta de teste "João Teste" | Administrador: excluir em **Usuários** |
| Número do grupo no nome do PDF de entrega | Equipe: informar o número para o arquivo final |
