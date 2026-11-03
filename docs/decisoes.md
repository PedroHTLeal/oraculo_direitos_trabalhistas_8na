# Registro de decisões e mudanças de escopo

Este documento reúne o que foi **pensado, testado e trocado** durante o desenvolvimento, com o motivo de cada escolha. Ele atende ao pedido da [Sprint 08](sprints/sprint-08/README.md) de registrar as mudanças de escopo. O restante da documentação descreve só o que o projeto usa hoje; aqui fica o caminho até lá.

Cada decisão aponta o commit em que a mudança entrou, para quem quiser ver o código daquele momento.

## Resumo

| Assunto | O que foi considerado | O que ficou | Principal motivo |
| --- | --- | --- | --- |
| Inteligência artificial | Claude (Anthropic) | Google Gemini, plano gratuito | Custo zero (RNF09) |
| Envio do conteúdo complementar | Twilio, WhatsApp Cloud API (Meta), n8n com WAHA e com Evolution API | E-mail pelo Gmail | Entregas falhando, regras de uso, instalação complexa e risco de bloqueio do número |
| Conta de usuário | Cadastro e login pelo telefone (WhatsApp) | Cadastro e login pelo e-mail | Acompanhou a troca do WhatsApp pelo e-mail |
| Sites e vídeos do "Saber mais" | Pesquisa no Google pelo Gemini e outras buscas automáticas | Links escolhidos pela equipe | Cota indisponível no plano gratuito e endereços inventados pela IA |
| Publicação na internet | GitHub Pages, Render | Vercel | Rodar o backend em Python e permitir envio de e-mail, sem custo |

## 1. Inteligência artificial: de Claude para Gemini

- **Primeira versão (31/10/2026, [`10f67db`](https://github.com/PedroHTLeal/oraculo_direitos_trabalhistas_8na/commit/10f67db)):** as respostas eram geradas pelo Claude, da Anthropic.
- **Problema:** a API do Claude é paga por uso, e o projeto tem como requisito não gerar custo (RNF09).
- **Decisão (31/10/2026, [`231dc75`](https://github.com/PedroHTLeal/oraculo_direitos_trabalhistas_8na/commit/231dc75)):** trocar pelo **Google Gemini**, que tem plano gratuito sem cartão de crédito. A forma de responder (só com os trechos da cartilha e com as fontes conferidas) continuou a mesma.
- **Ajuste posterior:** o modelo principal do plano gratuito às vezes fica sobrecarregado; nesse caso o sistema usa um modelo reserva do próprio Gemini ([`e5b69e5`](https://github.com/PedroHTLeal/oraculo_direitos_trabalhistas_8na/commit/e5b69e5)).

## 2. Envio do conteúdo complementar: do WhatsApp para o e-mail

A proposta da Sprint 01 previa enviar o "Saber mais" (resposta, 2 sites e 2 vídeos) e as novidades dos temas **pelo WhatsApp** (RF11, UC05, PB08). Foram testados quatro caminhos antes da troca para o e-mail.

### 2.1. Twilio (WhatsApp Sandbox)

- **Quando:** primeira versão, 31/10/2026 ([`10f67db`](https://github.com/PedroHTLeal/oraculo_direitos_trabalhistas_8na/commit/10f67db)).
- **Como funcionava:** a Twilio oferece um número de testes (Sandbox) que envia mensagens de WhatsApp por uma API.
- **Por que saiu:**
  - cada pessoa precisava primeiro mandar um **código de entrada** ("join ...") para o número da Twilio antes de receber qualquer mensagem, o que não faz sentido para o público do Oráculo;
  - depois do período de testes, o serviço é **pago** (RNF09).

### 2.2. WhatsApp Cloud API (API oficial da Meta)

- **Quando:** 02/11/2026 ([`f26a29a`](https://github.com/PedroHTLeal/oraculo_direitos_trabalhistas_8na/commit/f26a29a)).
- **Como funcionava:** a API oficial do WhatsApp, com um número de testes gratuito da Meta e um token de acesso.
- **O que aconteceu no teste real:** a Meta **aceitava** o envio, mas a mensagem **não chegava** ao celular. O número de teste estava cadastrado no WhatsApp sem o 9 extra dos celulares brasileiros, e o sistema da Meta não fazia essa correspondência.
- **Outras limitações:** o número de teste só envia para até 5 números cadastrados manualmente; fora da janela de 24 horas só podem ser enviados modelos de mensagem aprovados pela Meta; o token de acesso de teste expira.
- **Incidente de segurança:** durante a configuração, um token de acesso da Meta e uma chave de API foram parar no arquivo de exemplo do repositório. Os valores foram retirados ([`ec79687`](https://github.com/PedroHTLeal/oraculo_direitos_trabalhistas_8na/commit/ec79687), [`4795de3`](https://github.com/PedroHTLeal/oraculo_direitos_trabalhistas_8na/commit/4795de3)) e foi criado um teste automático que impede valores reais nos arquivos de exemplo.
- **Decisão da equipe:** não seguir com a API da Meta.

### 2.3. Automação no n8n com WAHA e com Evolution API

- **Quando:** 02/11/2026 ([`ca6c3dd`](https://github.com/PedroHTLeal/oraculo_direitos_trabalhistas_8na/commit/ca6c3dd) e [`2e4f094`](https://github.com/PedroHTLeal/oraculo_direitos_trabalhistas_8na/commit/2e4f094)).
- **Como funcionava:** o Oráculo avisava um fluxo do **n8n** (item PB09 do backlog, "Automação com n8n"), que enviava a mensagem por um conector de WhatsApp Web rodando no computador: primeiro o **WAHA**, depois a **Evolution API**, escolhida por ser muito usada no Brasil. O fluxo conferia como o número estava registrado no WhatsApp, o que resolvia o problema do 9 extra.
- **Por que saiu:**
  - exigia instalar e manter o **Docker Desktop** (com WSL 2 no Windows), um banco PostgreSQL e o n8n, além de ler um QR code com o celular: complexo para a equipe e para quem for avaliar;
  - só funcionava com o computador ligado, o que impediria publicar o sistema na internet;
  - o WhatsApp Web **não é um serviço oficial** para automação e vai contra os termos de uso do WhatsApp, com risco de **bloqueio do número**.

### 2.4. Decisão: e-mail pelo Gmail

- **Quando:** 02/11/2026 ([`e83e1ba`](https://github.com/PedroHTLeal/oraculo_direitos_trabalhistas_8na/commit/e83e1ba)).
- **Como funciona:** a pessoa informa **nome e e-mail** (com a autorização da LGPD) e recebe a resposta, os sites e os vídeos por e-mail. O envio usa uma conta do Gmail com **senha de app**, sem custo e sem instalar nada.
- **O que mudou junto:** a conta de usuário (Módulo 2) passou a usar e-mail e senha no lugar do telefone, e as novidades dos temas acompanhados também chegam por e-mail. O banco foi ajustado pelo [`006_contato_por_email.sql`](../supabase/006_contato_por_email.sql).
- **Requisitos afetados:** RF11, UC05, PB08 e PB09 foram atualizados no [relatório da Sprint 01](sprints/sprint-01/relatorio.md).
- **Teste real:** aprovado em 03/11/2026 (CT26 da [Sprint 09](sprints/sprint-09/README.md)).

## 3. Sites e vídeos do "Saber mais": da pesquisa automática para links escolhidos

- **Primeira ideia:** o próprio Gemini pesquisaria no Google 2 sites e 2 vídeos do YouTube sobre o assunto, e o sistema só aceitaria endereços que viessem da pesquisa real.
- **O que aconteceu no teste real:** a resposta do Gemini funcionou, mas a **pesquisa no Google não está liberada** no plano gratuito da chave usada (erro de cota).
- **Alternativas testadas e descartadas:**
  - pedir ao Gemini que sugerisse páginas oficiais sem pesquisar: das 6 sugeridas, **nenhuma existia** (endereços inventados pela IA);
  - ler páginas de resultados de buscadores: um deles bloqueia acesso automático, e esse tipo de leitura quebra quando o site muda.
- **Decisão (02/11/2026, [`24fee80`](https://github.com/PedroHTLeal/oraculo_direitos_trabalhistas_8na/commit/24fee80)):** a equipe escolhe e confere os links de cada assunto, que ficam na tabela `materiais_complementares` ([`007_materiais_complementares.sql`](../supabase/007_materiais_complementares.sql)). Para assuntos ainda sem links, vão a página da cartilha do TRT4, o texto oficial da lei e uma busca pronta no YouTube.
- **Ganhos:** endereços sempre reais e conferidos, envio mais rápido e sem depender de cota de API.

## 4. Publicação na internet

| Opção | Resultado |
| --- | --- |
| GitHub Pages (github.io) | Descartado: só hospeda páginas estáticas; não roda o backend em Python (IA, login, painel, e-mail) e não guarda chaves em segredo |
| Render (plano gratuito) | Descartado: o plano gratuito bloqueia o envio de e-mail, usado pelo "Saber mais" |
| **Vercel (plano Hobby)** | **Escolhido** ([`45176c3`](https://github.com/PedroHTLeal/oraculo_direitos_trabalhistas_8na/commit/45176c3)): gratuito, publica o site e o backend juntos a partir do GitHub, atualiza a cada envio e permite o e-mail. Guia em [`publicacao.md`](publicacao.md) |

Ajuste necessário: na Vercel o servidor "dorme" logo depois de responder, então lá o e-mail é enviado dentro do próprio pedido, em vez de depois da resposta.

## 5. Ajustes de usabilidade

As melhorias feitas depois da revisão da equipe com o sistema publicado (botão "Entrar" fora da consulta, fontes sem repetição e envio liberado só com o consentimento) estão na [Sprint 08](sprints/sprint-08/README.md#melhorias-de-usabilidade-revisão-da-equipe-03112026).
