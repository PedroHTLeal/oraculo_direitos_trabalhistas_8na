# Banco de dados (versão final)

O Oráculo usa o **Supabase**, um PostgreSQL gerenciado e gratuito. A estrutura é criada pelos scripts da pasta [`supabase/`](../supabase/), executados em ordem no **SQL Editor** do Supabase. Os diagramas (MER e modelo relacional) estão na [Sprint 02](sprints/sprint-02/diagramas.md).

## Scripts, na ordem de execução

| Script | O que faz |
| --- | --- |
| [`001_estrutura_inicial.sql`](../supabase/001_estrutura_inicial.sql) | Extensão `unaccent` e configuração de busca em português que ignora acentos (`pt_sem_acento`) |
| [`002_corrige_busca_e_sinonimos.sql`](../supabase/002_corrige_busca_e_sinonimos.sql) | Tabela de sinônimos com 41 expressões do dia a dia |
| [`003_modelo_relacional.sql`](../supabase/003_modelo_relacional.sql) | Modelo relacional completo: temas, trechos, perguntas, usuários, sessões, inscrições, atualizações e envios; função de busca |
| [`004_conta_com_whatsapp.sql`](../supabase/004_conta_com_whatsapp.sql) | Ajuste intermediário das contas (substituído pelo 006) |
| [`005_historico_de_operacoes.sql`](../supabase/005_historico_de_operacoes.sql) | Histórico de operações e índices do dashboard |
| [`006_contato_por_email.sql`](../supabase/006_contato_por_email.sql) | Contas e pedidos de "Saber mais" por e-mail |
| [`007_materiais_complementares.sql`](../supabase/007_materiais_complementares.sql) | Sites e vídeos do "Saber mais", escolhidos pela equipe |
| [`008_versao_final.sql`](../supabase/008_versao_final.sql) | Remove a última coluna sem uso e descreve cada tabela no próprio banco |

Depois dos scripts, `python backend/scripts/carregar_cartilha.py` carrega os 25 temas e 217 trechos da cartilha.

## Tabelas

| Tabela | Para que serve | Chave primária | Chaves estrangeiras e restrições |
| --- | --- | --- | --- |
| `temas` | As 25 páginas da cartilha do TRT4 | `id` | `nome` e `slug` únicos |
| `trechos` | Um subtítulo da cartilha, fonte das respostas | `id` | `tema_id` → `temas`; `atualizado_por` → `usuarios`; (`tema_id`, `ordem`) único |
| `sinonimos` | Palavras do dia a dia e os termos da cartilha | `termo` | — |
| `perguntas` | Perguntas e respostas, sem dados pessoais | `id` | — |
| `pergunta_trechos` | Fontes de cada resposta (N:N) | (`pergunta_id`, `trecho_id`) | → `perguntas`; → `trechos` |
| `solicitacoes_conteudo` | Pedidos de "Saber mais" | `id` | `pergunta_id` → `perguntas`; `consentimento` precisa ser verdadeiro; `status` em pendente, enviado ou erro |
| `materiais_enviados` | Sites e vídeos enviados em cada pedido | `id` | `solicitacao_id` → `solicitacoes_conteudo`; `tipo` em site ou video |
| `materiais_complementares` | Links escolhidos pela equipe por assunto | `id` | `tema_id` → `temas`; (`assunto`, `url`) único; `tipo` em site ou video |
| `usuarios` | Contas e perfis | `id` | e-mail único (sem diferenciar maiúsculas); `perfil` em administrador, curador ou usuario |
| `sessoes` | Logins ativos | `token_hash` | `usuario_id` → `usuarios` |
| `inscricoes_tema` | Temas que cada usuário acompanha | `id` | `tema_id` → `temas`; `usuario_id` → `usuarios`; (`tema_id`, e-mail) único |
| `atualizacoes` | Novidades publicadas pela equipe | `id` | `tema_id` → `temas`; `autor_id` → `usuarios` |
| `envios_atualizacao` | Envio de cada novidade a cada inscrito (N:N) | (`atualizacao_id`, `inscricao_id`) | → `atualizacoes`; → `inscricoes_tema`; `status` em pendente, enviado ou erro |
| `historico_operacoes` | Quem fez o quê e quando | `id` | `usuario_id` → `usuarios` (fica nulo se a conta for excluída; o nome é guardado) |

As colunas de cada tabela estão no [modelo relacional](sprints/sprint-02/diagramas.md#4-modelo-relacional).

## Regras garantidas pelo banco

- **Exclusões em cascata:** apagar um tema apaga os trechos e as inscrições dele; apagar uma pergunta apaga as fontes e os pedidos ligados a ela; apagar um usuário encerra as sessões.
- **Unicidade:** não há dois usuários com o mesmo e-mail, duas inscrições no mesmo tema com o mesmo e-mail nem o mesmo link duas vezes no mesmo assunto.
- **Valores permitidos:** perfis, situações de envio e tipos de material só aceitam os valores previstos.
- **Consentimento (LGPD):** um pedido de "Saber mais" só é gravado com a autorização marcada.

## Busca na cartilha

- A coluna `trechos.busca` guarda o índice de busca (tsvector), mantido por gatilho a cada inclusão ou alteração; o tema e o subtítulo pesam mais que o texto.
- A função `buscar_trechos(consulta, limite)` ignora acentos, acrescenta os sinônimos e devolve os trechos candidatos; o backend reordena dando mais peso às palavras raras ([`ranqueamento.py`](../backend/app/ranqueamento.py)).
- Índices: GIN em `trechos.busca`, e índices por data em `perguntas`, `solicitacoes_conteudo` e `historico_operacoes` para o dashboard.

## Segurança (RNF03)

- Todas as tabelas têm **RLS** (segurança por linha) ativado e nenhuma política pública: só o backend, com a chave de serviço, lê e grava os dados. Ninguém acessa o banco direto pelo navegador.
- Senhas guardadas só como hash (scrypt); sessões guardam só o hash do token.
- As chaves ficam no `backend/.env` e nas variáveis da Vercel, nunca no repositório (um teste automático confere isso).

## Manutenção no plano gratuito

O Supabase gratuito **pausa o projeto depois de 7 dias sem uso**. Para evitar isso, a rotina [`manter-ativo.yml`](../.github/workflows/manter-ativo.yml) do GitHub Actions consulta a lista de temas do site publicado a cada 2 dias, o que usa o banco e o mantém ativo; se o site ou o banco estiverem fora do ar, a rotina falha e o GitHub avisa por e-mail. Se mesmo assim o site mostrar "Ocorreu um erro inesperado" ao listar os temas, entre em https://supabase.com/dashboard, abra o projeto e clique em **Restore project** (leva alguns minutos). Os dados continuam salvos.
