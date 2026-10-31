# Oráculo dos Direitos Trabalhistas

**Sprint 01: Planejamento Inicial do Projeto**
Ciência da Computação 8NA · Apresentado para Pryscilla de Barros Gonçalves
Preparado pela equipe Kaleido Void Studios

> Versão atualizada do relatório da Sprint 01, mantida junto com o código. As mudanças em relação à versão entregue estão no [histórico de alterações](#histórico-de-alterações) no fim do documento.

## Índice

1. Identificação da Equipe
2. Escolha do Tema
3. Definição do Problema
4. Objetivos
   - 4.1. Objetivo geral
   - 4.2. Objetivos específicos
   - 4.3. Resultados esperados
5. Público-alvo
6. Requisitos Funcionais
7. Requisitos Não Funcionais
8. Casos de Uso
   - 8.1. Atores
   - 8.2. Casos de uso do Usuário
   - 8.3. Casos de uso do Administrador
9. Product Backlog Inicial
10. Cronograma Inicial
11. Repositório GitHub
12. Tecnologias Definidas
13. Andamento do Desenvolvimento
14. Identidade Visual

## 1. Identificação da Equipe

- **Curso:** Ciência da Computação
- **Turma:** 8NA
- **Disciplinas:** Fábrica de Software, Tópicos Avançados e DevOps Tools
- **Projeto:** Oráculo dos Direitos Trabalhistas
- **Repositório:** https://github.com/PedroHTLeal/oraculo_direitos_trabalhistas_8na
- **Integrantes:** Pedro Henrique Tenório Leal - 01591056 - 8NA

## 2. Escolha do Tema

A proposta é desenvolver uma plataforma capaz de receber dúvidas dos usuários em linguagem natural e apresentar respostas de forma mais simples e acessível, utilizando como base conteúdos de fontes confiáveis, inicialmente tendo como referência a Cartilha de Direitos e Obrigações no Trabalho do Tribunal Regional do Trabalho da 4ª Região (TRT4).

O sistema utilizará uma abordagem baseada em RAG (Retrieval-Augmented Generation), buscando informações relevantes na base de conhecimento antes da geração da resposta.

O projeto está inserido na área de Tecnologia da Informação aplicada ao acesso à informação sobre direitos e obrigações trabalhistas, utilizando recursos de Inteligência Artificial para facilitar a consulta e a compreensão de conteúdos relacionados ao tema.

Dessa forma, o mesmo projeto será utilizado pelas três disciplinas, com diferentes enfoques dentro do processo de desenvolvimento:

- **Fábrica de Software:** organização e gestão do desenvolvimento;
- **Tópicos Avançados:** Inteligência Artificial, RAG, LLM e avaliação das respostas;
- **DevOps Tools:** versionamento, integração, testes, automação e entrega do software.

## 3. Definição do Problema

O acesso a informações sobre direitos e obrigações trabalhistas pode ser dificultado pela utilização de termos jurídicos, pela quantidade de informações disponíveis e pela dificuldade de localizar e interpretar conteúdos confiáveis. Esse problema pode afetar especialmente pessoas que possuem pouca familiaridade com informações jurídicas ou com ferramentas digitais, dificultando a compreensão de situações relacionadas ao trabalho.

Entre os públicos que podem encontrar essas dificuldades estão trabalhadores informais ou de aplicativos, trabalhadores domésticos, pessoas com menor escolaridade e jovens que estão ingressando no mercado de trabalho, incluindo estudantes e estagiários.

Diante disso, surge a necessidade de uma solução que facilite a busca e a compreensão dessas informações, utilizando uma linguagem mais acessível e mantendo a indicação da fonte utilizada.

O problema central do projeto pode ser definido como:

> Como facilitar o acesso e a compreensão de informações sobre direitos e obrigações trabalhistas por meio de uma plataforma digital que permita ao usuário realizar perguntas em linguagem natural e obter respostas baseadas em fontes confiáveis?

## 4. Objetivos

### 4.1. Objetivo geral

Facilitar o acesso à informação sobre direitos e obrigações trabalhistas por meio de uma plataforma com Inteligência Artificial capaz de responder dúvidas em linguagem acessível, utilizando fontes confiáveis.

### 4.2. Objetivos específicos

- Permitir que o usuário realize perguntas utilizando linguagem natural.
- Facilitar a localização de informações relacionadas aos direitos e obrigações trabalhistas.
- Utilizar uma base de conhecimento confiável para fundamentar as respostas.
- Aplicar uma abordagem de RAG para recuperar informações relevantes antes da geração da resposta.
- Apresentar as respostas em linguagem mais simples e compreensível.
- Informar a fonte utilizada para cada resposta.
- Permitir que o usuário consulte o conteúdo original utilizado como referência.
- Evitar que a Inteligência Artificial forneça respostas sem informações suficientes na base de conhecimento.
- Permitir que o usuário solicite conteúdos complementares por meio do WhatsApp.
- Permitir que o usuário escolha temas para acompanhar e receber atualizações.

### 4.3. Resultados esperados

Espera-se que o sistema facilite o acesso a informações trabalhistas, reduza a dificuldade de interpretação de conteúdos jurídicos e permita que o usuário encontre informações relevantes de maneira simples e direta.

Também se espera criar uma estrutura que permita a evolução da plataforma durante as próximas Sprints, incluindo o desenvolvimento da aplicação, integração com banco de dados, Inteligência Artificial, WhatsApp e práticas de DevOps.

## 5. Público-alvo

O público-alvo principal do sistema são trabalhadores que desejam obter informações sobre seus direitos e obrigações trabalhistas.

O projeto terá atenção especial para:

- trabalhadores informais e trabalhadores de aplicativos;
- trabalhadores domésticos;
- pessoas com menor familiaridade com termos jurídicos;
- pessoas com menor familiaridade com ferramentas digitais;
- jovens em seu primeiro contato com o mercado de trabalho;
- estudantes e estagiários.

A interface deverá priorizar simplicidade, clareza e facilidade de utilização, permitindo que o usuário consiga realizar uma consulta sem a necessidade de possuir conhecimentos técnicos ou jurídicos.

## 6. Requisitos Funcionais

| ID | Requisito | Situação |
| --- | --- | --- |
| RF01 | O sistema deverá permitir o acesso às funcionalidades básicas sem a necessidade de criação de uma conta. | Atendido |
| RF02 | O sistema deverá apresentar perguntas e temas sugeridos na página inicial. | Atendido |
| RF03 | O sistema deverá permitir que o usuário digite uma pergunta livremente. | Atendido |
| RF04 | O sistema deverá utilizar uma abordagem RAG para buscar informações relevantes na base de conhecimento. | Implementado (teste real pendente) |
| RF05 | O sistema deverá gerar respostas utilizando as informações recuperadas da base de conhecimento. | Implementado (teste real pendente) |
| RF06 | O sistema deverá apresentar as respostas em linguagem acessível ao usuário. | Implementado (teste real pendente) |
| RF07 | O sistema deverá informar a fonte utilizada para a resposta. | Implementado (teste real pendente) |
| RF08 | O sistema deverá permitir que o usuário consulte o conteúdo original utilizado como referência. | Implementado (teste real pendente) |
| RF09 | O sistema deverá informar quando não encontrar informações suficientes na base de conhecimento para responder à pergunta. | Implementado (teste real pendente) |
| RF10 | O sistema deverá permitir que o usuário solicite informações complementares sobre o assunto pesquisado. | Implementado (teste real pendente) |
| RF11 | O sistema deverá permitir o envio de conteúdos complementares por meio do WhatsApp quando solicitado pelo usuário. | Implementado (teste real pendente) |
| RF12 | O sistema deverá permitir que o usuário selecione temas para acompanhar. | Não iniciado |
| RF13 | O sistema deverá permitir o envio de atualizações relacionadas aos temas selecionados pelo usuário. | Não iniciado |
| RF14 | O sistema deverá possuir uma área administrativa. | Não iniciado |

## 7. Requisitos Não Funcionais

| ID | Requisito |
| --- | --- |
| RNF01 | O sistema deverá ser acessível por computadores e dispositivos móveis. |
| RNF02 | A interface deverá priorizar uma experiência simples e acessível, principalmente em dispositivos móveis. |
| RNF03 | O sistema deverá adotar medidas relacionadas à proteção dos dados dos usuários, considerando os princípios da LGPD. |
| RNF04 | A área administrativa deverá possuir mecanismo de autenticação. |
| RNF05 | O sistema deverá apresentar um tempo de resposta aceitável para as consultas realizadas pelo usuário. |
| RNF06 | O sistema deverá possuir mecanismos de registro de erros para facilitar a identificação de problemas. |
| RNF07 | O sistema deverá permanecer disponível para utilização contínua, dentro das condições de infraestrutura definidas durante o desenvolvimento. |
| RNF08 | As respostas geradas pela Inteligência Artificial deverão buscar consistência e aderência às informações existentes na base de conhecimento. |
| RNF09 | A solução deverá considerar o custo operacional relacionado ao uso dos recursos de Inteligência Artificial e das integrações externas. |
| RNF10 | O código-fonte deverá utilizar um sistema de controle de versão para registrar e acompanhar as alterações realizadas pela equipe. |
| RNF11 | O projeto deverá possuir organização adequada do repositório para facilitar o trabalho colaborativo entre os integrantes. |
| RNF12 | O processo de desenvolvimento deverá contemplar testes e validações antes da disponibilização de novas versões do sistema. |
| RNF13 | Sempre que tecnicamente viável, etapas de integração, testes e disponibilização deverão ser automatizadas. |
| RNF14 | O sistema deverá possuir um processo organizado de implantação e atualização de suas versões. |

Observação: as tecnologias da aplicação já foram definidas (seção 12). As ferramentas específicas de integração contínua, deploy e monitoramento ainda serão definidas durante as próximas Sprints.

## 8. Casos de Uso

### 8.1. Atores

O sistema terá inicialmente dois atores principais:

- **Usuário:** pessoa que acessa a plataforma para consultar informações sobre direitos e obrigações trabalhistas.
- **Administrador:** responsável pela manutenção da base de conhecimento e pela auditoria das informações geradas pelo sistema.

### 8.2. Casos de uso do Usuário

| ID | Caso de uso | Descrição |
| --- | --- | --- |
| UC01 | Realizar pergunta | O usuário informa uma dúvida sobre direitos ou obrigações trabalhistas. |
| UC02 | Receber resposta | O sistema processa a pergunta, consulta a base de conhecimento e apresenta uma resposta acessível. |
| UC03 | Consultar fonte | O usuário pode visualizar a fonte utilizada para fundamentar a resposta. |
| UC04 | Solicitar conteúdo complementar | O usuário solicita informações adicionais relacionadas ao assunto consultado. |
| UC05 | Receber conteúdo pelo WhatsApp | O usuário fornece as informações necessárias para receber conteúdos complementares por WhatsApp. |
| UC06 | Acompanhar tema | O usuário seleciona um tema para receber futuras atualizações relacionadas a ele. |

### 8.3. Casos de uso do Administrador

| ID | Caso de uso | Descrição |
| --- | --- | --- |
| UC07 | Atualizar base de conhecimento | O administrador adiciona, atualiza ou remove conteúdos utilizados pelo sistema. |
| UC08 | Auditar perguntas | O administrador consulta os registros de perguntas para acompanhar o funcionamento do sistema, sem expor dados sensíveis dos usuários. |

## 9. Product Backlog Inicial

O Product Backlog representa as principais atividades e funcionalidades planejadas para a evolução do projeto.

| ID | Item | Descrição | Área | Situação |
| --- | --- | --- | --- | --- |
| PB01 | Levantamento de requisitos | Definir e documentar as necessidades do sistema. | Fábrica de Software | Concluído |
| PB02 | Modelagem do banco de dados | Estruturar as informações que serão armazenadas pelo sistema. | Desenvolvimento | Concluído |
| PB03 | Desenvolvimento do backend | Criar a estrutura responsável pelo processamento das requisições. | Desenvolvimento | Em andamento |
| PB04 | Desenvolvimento do frontend | Criar a interface de interação com o usuário. | Desenvolvimento | Em andamento |
| PB05 | Construção da base de conhecimento | Organizar os conteúdos utilizados pelo sistema. | Tópicos Avançados | Concluído |
| PB06 | Implementação do RAG | Desenvolver o mecanismo de recuperação das informações relevantes. | Tópicos Avançados | Em andamento |
| PB07 | Integração com banco de dados | Integrar a aplicação à estrutura de armazenamento. | Desenvolvimento | Em andamento |
| PB08 | Integração com WhatsApp | Criar o fluxo para envio de conteúdos complementares e atualizações. | Integração | Em andamento |
| PB09 | Automação com n8n | Estruturar as automações relacionadas às integrações externas. | Integração / DevOps | Não iniciado |
| PB10 | Área administrativa | Desenvolver as funcionalidades para manutenção da base e auditoria. | Desenvolvimento | Não iniciado |
| PB11 | Testes do sistema | Verificar o funcionamento das funcionalidades e integrações. | DevOps Tools | Em andamento |
| PB12 | Avaliação das respostas da IA | Verificar a consistência das respostas e sua relação com a base de conhecimento. | Tópicos Avançados | Não iniciado |
| PB13 | Integração geral | Integrar frontend, backend, banco de dados, IA e WhatsApp. | DevOps Tools | Não iniciado |
| PB14 | Deploy | Preparar o sistema para disponibilização em ambiente de execução. | DevOps Tools | Não iniciado |
| PB15 | Documentação | Registrar o desenvolvimento, decisões e funcionamento do projeto. | Fábrica de Software | Em andamento |
| PB16 | Controle de versões | Organizar o código e acompanhar as alterações realizadas pela equipe. | DevOps Tools | Em andamento |
| PB17 | Organização do repositório | Definir uma estrutura adequada para branches, commits e arquivos do projeto. | DevOps Tools | Em andamento |
| PB18 | Automação de testes | Estruturar a execução automatizada de testes durante o desenvolvimento. | DevOps Tools | Em andamento |
| PB19 | Integração contínua | Automatizar a validação das alterações realizadas no projeto. | DevOps Tools | Não iniciado |
| PB20 | Deploy automatizado | Estruturar o processo de disponibilização de novas versões da aplicação. | DevOps Tools | Não iniciado |
| PB21 | Monitoramento e logs | Registrar informações importantes para identificação de erros e acompanhamento do sistema. | DevOps Tools | Em andamento |

## 10. Cronograma Inicial

O desenvolvimento será realizado de forma incremental, utilizando Sprints para organizar a evolução do projeto.

| Sprint | Atividades |
| --- | --- |
| Sprint 01 | Requisitos, casos de uso, backlog e planejamento; definição da proposta de IA/RAG; organização do repositório e controle de versão |
| Sprint 02 | Planejamento das funcionalidades; preparação da base de conhecimento; estruturação do ambiente de desenvolvimento *(adiantada: já concluída na Sprint 01)* |
| Sprint 03 | Desenvolvimento do sistema; integração do código e testes *(iniciado: tela de perguntas já desenvolvida)* |
| Sprint 04 | Integração das funcionalidades; implementação do RAG/IA; automação de testes e integração |
| Sprint 05 | Integração geral; ajustes e avaliação da IA; integrações e automações |
| Sprint 06 | Testes e preparação da entrega; avaliação das respostas; deploy, monitoramento e versão final |

Observação: o cronograma é inicial e poderá ser ajustado conforme o andamento do projeto e as orientações realizadas durante as próximas Sprints.

## 11. Repositório GitHub

O projeto possui um repositório no GitHub destinado ao armazenamento e controle de versão dos arquivos desenvolvidos pela equipe.

**Repositório:** https://github.com/PedroHTLeal/oraculo_direitos_trabalhistas_8na

O GitHub é utilizado para organização do código, controle de versões, colaboração entre os integrantes e acompanhamento da evolução do projeto.

**Estrutura do repositório:**

```
backend/    API em Python (FastAPI), testes, scripts e dados da cartilha
frontend/   Interface web em React
supabase/   Estrutura do banco de dados (SQL)
docs/       Documentação do projeto, guia de configuração e relatórios das Sprints
```

**Estratégia de branches:**

- `main` é o branch principal e contém sempre a versão estável do projeto;
- cada funcionalidade é desenvolvida em um branch próprio, criado a partir do `main` (por exemplo, `tela-perguntas`);
- ao final, a funcionalidade é enviada ao GitHub e integrada ao `main` por meio de um **Pull Request**, que registra as alterações e permite sua revisão antes da integração;
- cada versão enviada é registrada no arquivo `CHANGELOG.md`, com data, objetivo, o que foi feito e como agrega ao projeto.

A definição das automações de integração contínua e deploy será realizada durante as próximas Sprints.

## 12. Tecnologias Definidas

| Camada | Tecnologia | Motivo |
| --- | --- | --- |
| Backend | Python 3.12 + FastAPI | Python concentra as principais bibliotecas de IA e RAG; FastAPI é leve, rápido e gera documentação da API automaticamente. |
| Frontend | React + Vite | Componentes reutilizáveis e ambiente de desenvolvimento rápido, com interface responsiva para celular e computador. |
| Testes do backend | pytest | Ferramenta padrão de testes em Python, base para a automação de testes (PB18). |
| Qualidade do frontend | ESLint | Verificação automática de padrões e erros no código React. |
| Controle de versão | Git + GitHub | Versionamento e colaboração (RNF10, RNF11). |
| Banco de dados | Supabase (PostgreSQL) | Banco gerenciado e gratuito no início, com busca textual em português (ignorando acentos) e controle de acesso por tabela (RNF03). |
| Inteligência Artificial | Claude Opus 5.5 (Anthropic) | Gera respostas em linguagem simples usando só os trechos da cartilha e pesquisa na web os sites e vídeos complementares, sem precisar de outras APIs de busca. |
| WhatsApp | Twilio (Sandbox) | Ambiente de teste gratuito para enviar mensagens de WhatsApp, adequado para a demonstração do projeto. |

As ferramentas de integração contínua e deploy serão definidas nas próximas Sprints.

## 13. Andamento do Desenvolvimento

### Tela de perguntas

Primeira tela do sistema, que atende ao caso de uso UC01 (Realizar pergunta):

- campo para o usuário digitar a pergunta livremente, com limite de 500 caracteres (RF03);
- temas e perguntas sugeridos na página inicial — Férias, 13º salário, Jornada de trabalho, Rescisão, Estágio e Trabalho doméstico (RF02);
- acesso sem criação de conta (RF01);
- cartão de resposta preparado para exibir a fonte e o link para o conteúdo original (RF07, RF08);
- aviso destacado quando não há informação suficiente na base de conhecimento (RF09);
- layout adaptado para celular e computador (RNF01, RNF02);
- aviso de que as respostas têm caráter informativo.

Na primeira versão, a API respondia que ainda não havia informações suficientes, já no formato final (resposta, fontes e indicação se encontrou). Com isso, a tela não precisou mudar quando a IA foi conectada (ver "Base de conhecimento, IA e WhatsApp" abaixo).

### Base de conhecimento, IA e WhatsApp

**Base de conhecimento (PB05):** um script extrai automaticamente as 25 páginas da Cartilha de Direitos e Obrigações no Trabalho do TRT4 e as divide em 217 trechos, um por subtítulo, cada um com o tema, a seção e o link da página original. Os trechos ficam salvos no repositório (`backend/dados/cartilha.json`) e são carregados no Supabase.

**Banco de dados (PB02, PB07):** o Supabase guarda três tabelas:

| Tabela | Conteúdo |
| --- | --- |
| `trechos` | Os trechos da cartilha, com um índice de busca em português que ignora acentos |
| `perguntas` | As perguntas feitas e as respostas geradas, para auditoria (UC08), sem dados pessoais |
| `solicitacoes_whatsapp` | Os pedidos de conteúdo pelo WhatsApp: telefone, consentimento, situação do envio e materiais enviados |

O acesso às tabelas é bloqueado para o público; só o backend, com a chave de serviço, lê e grava os dados (RNF03).

**Como a resposta é gerada (RAG, PB06):**

1. A pergunta é usada para buscar no Supabase os 6 trechos mais relevantes (busca textual; palavras no tema e no subtítulo pesam mais).
2. A IA recebe somente esses trechos e escreve uma resposta curta e simples (RF05, RF06), indicando quais trechos usou.
3. O sistema confere se os trechos citados vieram mesmo da busca e os mostra como fonte, com o texto original e o link para a cartilha (RF07, RF08).
4. Se nenhum trecho for encontrado, ou se a IA concluir que eles não respondem à pergunta, a tela informa que não há informação suficiente (RF09).

Em computadores, a resposta aparece no painel azul, no lugar da órbita de temas; no celular, logo abaixo do campo de pergunta.

**Saiba mais pelo WhatsApp (RF10, RF11, UC04, UC05, PB08):**

1. Abaixo da resposta, o botão "Saiba mais pelo WhatsApp" abre uma janela que pede o telefone com DDD e o consentimento para o uso do número, conforme a LGPD (RNF03).
2. O backend registra o pedido e, em segundo plano, a IA pesquisa na web 2 sites confiáveis e 2 vídeos do YouTube sobre o assunto. Só são aceitos links que apareceram de fato na pesquisa.
3. A Twilio envia ao WhatsApp do usuário a resposta, os 2 sites e os 2 vídeos. A tela acompanha o envio e confirma quando ele termina.

**Registro de erros (RNF06, PB21):** falhas na IA, no banco ou no envio do WhatsApp são registradas no log do servidor, e um pedido que falha fica marcado como "erro" no banco, sem ficar pendente para sempre.

**Situação:** a funcionalidade está implementada e testada com versões simuladas do banco, da IA e do WhatsApp. O teste com os serviços reais depende da criação das contas no Supabase, na Anthropic e na Twilio, descrita em `docs/configuracao.md`.

**Testes automatizados do backend:** 35 testes, cobrindo a busca e a geração da resposta, as fontes exibidas, o caso sem informação, o pedido pelo WhatsApp (consentimento, telefone inválido, falha na pesquisa), a validação de telefones, a filtragem dos links e vídeos e o tamanho da mensagem.

### Novo visual

A tela de perguntas recebeu a identidade visual descrita na seção 14. Em computadores, a tela é dividida em duas partes: à esquerda, o conteúdo (pergunta, resposta e temas); à direita, um painel azul com os temas girando em órbita ao redor de uma balança da justiça e uma frase sobre o propósito do sistema. No celular, o painel azul é ocultado para priorizar o conteúdo (RNF02). Os temas sugeridos passaram a ser exibidos como cartões.

## 14. Identidade Visual

| Elemento | Definição |
| --- | --- |
| Logotipo | Símbolo circular em azul-escuro com um ponto dourado, seguido do nome "Oráculo" e do complemento "Direitos Trabalhistas" |
| Fonte | Plus Jakarta Sans (pesos 400 a 800) |
| Azul-escuro `#030C2C` | Cor principal: botões, tema selecionado, painel lateral e indicador de foco para navegação por teclado |
| Dourado `#E8B20F` | Cor de destaque: núcleo da órbita, ponto do logotipo, detalhes do tema selecionado e botão "Perguntar" ao passar o mouse |
| Texto `#1C1C1C` / `#5C5C5C` | Texto principal e texto de apoio |
| Bordas `#E2E2E2` | Cartões e campos, com cantos arredondados de 14px |
| Símbolo | Balança da justiça, representando direitos e equilíbrio nas relações de trabalho |

Princípios aplicados: muito espaço em branco, títulos fortes, poucos elementos por tela, áreas de toque de no mínimo 44px para uso no celular e animação desativada automaticamente para quem configura o sistema para reduzir movimento (acessibilidade).

## Histórico de alterações

| Data | Alteração |
| --- | --- |
| 31/10/2026 | Seção 4 renomeada de "Identidade Visual" para "Objetivos", com a numeração 4.1, 4.2 e 4.3 alinhada ao conteúdo. A identidade visual passou a ter seção própria (14). |
| 31/10/2026 | Seções 6 e 9: incluída a coluna "Situação" em requisitos funcionais e backlog. |
| 31/10/2026 | Seção 7: observação atualizada, pois as tecnologias da aplicação foram definidas. |
| 31/10/2026 | Seção 10: Sprint 02 marcada como adiantada e Sprint 03 como iniciada. |
| 31/10/2026 | Seção 11: incluídas a estrutura do repositório, a estratégia de branches com Pull Requests e o registro de versões no CHANGELOG. |
| 31/10/2026 | Novas seções 12 (Tecnologias Definidas) e 13 (Andamento do Desenvolvimento). |
| 31/10/2026 | Nova seção 14 (Identidade Visual) e descrição do novo visual na seção 13. |
| 31/10/2026 | Seção 14: paleta alterada para azul-escuro `#030C2C` e dourado `#E8B20F`. |
| 31/10/2026 | Seções 6, 9, 11, 12 e 13: base de conhecimento no Supabase, respostas com IA e envio de conteúdo pelo WhatsApp. |
