# Sprint 02 — Arquitetura, modelagem e protótipos

**Situação:** Em andamento: banco e estrutura prontos; diagramas e documento técnico em elaboração · [← Voltar ao índice](../../README.md)

## O que a Sprint pediu

Transformar o planejamento em estrutura técnica: arquitetura do sistema, diagrama de classes, modelo entidade-relacionamento (MER), modelo relacional, protótipos das telas principais, banco de dados criado e projeto organizado no GitHub.

## O que foi entregue

| Item pedido | Entrega | Situação | Onde ver |
| --- | --- | --- | --- |
| Arquitetura do sistema | Frontend React → API FastAPI → Supabase (PostgreSQL), Google Gemini e Twilio | Implementada; diagrama em elaboração | [README principal](../../../README.md#como-funciona) |
| Diagrama de classes | Classes de domínio e de serviço do backend | Em elaboração | — |
| MER | Entidades: tema, trecho, pergunta, usuário, sessão, inscrição, atualização, envio, solicitação, material, histórico | Em elaboração | — |
| Modelo relacional | 13 tabelas com chaves primárias e estrangeiras | Implementado no banco; diagrama em elaboração | [Scripts SQL](../../../supabase/) |
| Protótipo das telas | Telas funcionais no próprio sistema (consulta, resposta, Saiba mais) | Concluído | [Identidade visual, seção 14](../sprint-01/relatorio.md#14-identidade-visual) |
| Banco de dados criado | Supabase com a cartilha do TRT4 carregada (25 temas, 217 trechos) | Concluído | [supabase/](../../../supabase/) |
| Projeto no GitHub | Estrutura `backend/`, `frontend/`, `supabase/` e `docs/` | Concluído | [Repositório](https://github.com/PedroHTLeal/oraculo_direitos_trabalhistas_8na) |

## Ajustes desta Sprint

| Commit | O que mudou |
| --- | --- |
| [`6824b07`](https://github.com/PedroHTLeal/oraculo_direitos_trabalhistas_8na/commit/6824b07) | Backend em Python/FastAPI e frontend em React/Vite |
| [`438333f`](https://github.com/PedroHTLeal/oraculo_direitos_trabalhistas_8na/commit/438333f) | Primeira tela: perguntas, temas sugeridos e cartão de resposta |
| [`2392fd3`](https://github.com/PedroHTLeal/oraculo_direitos_trabalhistas_8na/commit/2392fd3) | Identidade visual inspirada no FlowFocus (layout dividido e painel com órbitas) |
| [`6e6f5a2`](https://github.com/PedroHTLeal/oraculo_direitos_trabalhistas_8na/commit/6e6f5a2) | Paleta definitiva: azul-escuro `#030C2C` e dourado `#E8B20F` |
| [`10f67db`](https://github.com/PedroHTLeal/oraculo_direitos_trabalhistas_8na/commit/10f67db) | Extração da cartilha do TRT4 e primeira estrutura do banco no Supabase |
| [`1c4b4a9`](https://github.com/PedroHTLeal/oraculo_direitos_trabalhistas_8na/commit/1c4b4a9) | Busca validada no banco real, correção da busca e tabela de sinônimos |
| [`ecd1787`](https://github.com/PedroHTLeal/oraculo_direitos_trabalhistas_8na/commit/ecd1787) | Modelo relacional completo (temas, usuários, perfis, sessões, inscrições, atualizações) |

## Mudanças em relação ao planejado

- **Banco de dados:** foi escolhido o Supabase (PostgreSQL gerenciado e gratuito), com busca textual em português no lugar de um banco vetorial. A cartilha tem apenas 217 trechos, e a busca textual com sinônimos se mostrou suficiente e sem custo.
- **Protótipos:** em vez de um protótipo no Figma, a equipe construiu as telas direto no sistema, que já funcionam como protótipo navegável.

## Pendências

- Diagramas de arquitetura, de classes, MER e relacional, com explicação de cada um, no documento técnico desta Sprint.
