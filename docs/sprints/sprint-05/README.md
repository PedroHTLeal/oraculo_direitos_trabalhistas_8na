# Sprint 05 — Módulo 2: acompanhamento pelo WhatsApp

**Situação:** Concluída no código; teste com o banco real aguarda os scripts SQL 004 e 005 · [← Voltar ao índice](../../README.md)

## O que a Sprint pediu

Segundo módulo completo, integrado ao banco de dados, com regras de negócio atualizadas, testes das funcionalidades e correção dos bugs encontrados.

## Módulo entregue: acompanhamento de temas pelo WhatsApp

**Fluxo completo:** a pessoa cria a conta com o WhatsApp → escolhe temas para acompanhar → a equipe publica uma atualização do tema → o sistema envia a mensagem a cada inscrito e registra a situação de cada envio → a pessoa também vê a novidade em **Meus temas**.

## O que foi entregue

| Item pedido | Entrega | Onde ver |
| --- | --- | --- |
| Segundo módulo | Conta com WhatsApp, temas acompanhados e atualizações | Telas **Cadastre seu WhatsApp**, **Meus temas** e **Atualizações** |
| Integração com o banco | Tabelas `usuarios`, `inscricoes_tema`, `atualizacoes` e `envios_atualizacao` | [`supabase/004_conta_com_whatsapp.sql`](../../../supabase/004_conta_com_whatsapp.sql) |
| Regras de negócio | Ver tabela abaixo | [`rotas/atualizacoes.py`](../../../backend/app/rotas/atualizacoes.py) |
| Testes | 97 testes automatizados no backend (`pytest`) | [`backend/tests/`](../../../backend/tests/) |
| Correção de bugs | Ver tabela de bugs abaixo | — |

### Regras de negócio implementadas ou atualizadas

| Regra | Justificativa |
| --- | --- |
| O cadastro público usa **nome, WhatsApp e senha**, com autorização obrigatória (LGPD) | A conta existe para a pessoa receber conteúdo pelo WhatsApp (mudança pedida pela equipe) |
| A equipe entra com **e-mail**; usuários comuns, com o **telefone** | Cada público usa o dado que já tem |
| Só recebem a atualização as **inscrições ativas** do tema no momento da publicação | Evita mensagens a quem deixou de acompanhar |
| O **curador só exclui as próprias** publicações; o administrador exclui qualquer uma | Responsabilidade sobre o que foi publicado |
| A publicação é salva **mesmo sem o WhatsApp configurado**; os envios ficam com erro e podem ser reenviados | Nenhuma informação se perde por falha externa |
| Uma pessoa não acompanha o mesmo tema duas vezes | Evita mensagens duplicadas |

### Bugs encontrados e corrigidos

| Bug | Causa | Correção |
| --- | --- | --- |
| A busca não encontrava "estágio" nem com a palavra exata | A função SQL processava as palavras da pergunta duas vezes | Função corrigida ([`002`](../../../supabase/002_corrige_busca_e_sinonimos.sql)) |
| "Demitido", "patrão" e "FGTS" não achavam os temas certos | A cartilha usa outras palavras ("dispensa", "empregador") | Tabela de sinônimos editável |
| Erro 500 intermitente ao abrir a base | O Supabase encerra conexões paradas | Repetição automática da operação ([`4165443`](https://github.com/PedroHTLeal/oraculo_direitos_trabalhistas_8na/commit/4165443)) |
| Cadastros de teste recusados | O validador de e-mail não aceita o domínio reservado `.test` | Testes com domínio válido |
| Filtro de período do dashboard sempre recusado | O valor chega como texto e não era convertido | Validação própria com mensagem clara |

## Ajustes desta Sprint

| Commit | O que mudou |
| --- | --- |
| [`43414b5`](https://github.com/PedroHTLeal/oraculo_direitos_trabalhistas_8na/commit/43414b5) | Cadastro e login por telefone; "Saiba mais" e temas usam o telefone da conta |
| [`7f76733`](https://github.com/PedroHTLeal/oraculo_direitos_trabalhistas_8na/commit/7f76733) | Telas de conta com WhatsApp e "Saiba mais" com criar conta / entrar |
| [`7f43866`](https://github.com/PedroHTLeal/oraculo_direitos_trabalhistas_8na/commit/7f43866) | Módulo 2 no backend: publicar, enviar, reenviar e excluir atualizações |
| [`e24c793`](https://github.com/PedroHTLeal/oraculo_direitos_trabalhistas_8na/commit/e24c793) | Telas do Módulo 2: Atualizações e novidades em Meus temas |
