# Documentação do Oráculo dos Direitos Trabalhistas

Esta pasta reúne tudo o que foi pedido e entregue em cada Sprint das disciplinas de **Fábrica de Software**, **Tópicos Avançados** e **DevOps Tools** (Ciência da Computação, turma 8NA).

## Como navegar

1. Veja na tabela abaixo a **situação de cada Sprint**.
2. Abra a Sprint: cada página segue o mesmo roteiro: **o que foi pedido → o que foi entregue → ajustes (commits) → evidências → pendências**.
3. Cada ajuste tem um link para o commit no GitHub, onde é possível ver exatamente o que mudou no código.

## Sprints

| Sprint | Tema | Situação | Principais entregas |
| --- | --- | --- | --- |
| [01](sprints/sprint-01/README.md) | Planejamento inicial | Concluída | Requisitos, casos de uso, backlog, cronograma · [relatório completo](sprints/sprint-01/relatorio.md) |
| [02](sprints/sprint-02/README.md) | Arquitetura, modelagem e protótipos | Concluída | Banco no Supabase com a cartilha do TRT4, diagramas de arquitetura, classes, MER e relacional, telas e identidade visual |
| [03](sprints/sprint-03/README.md) | Base funcional | Concluída | Login, cadastro, perfis, CRUD da base de conhecimento e deploy local |
| [04](sprints/sprint-04/README.md) | Módulo 1: gestão da base de conhecimento | Concluída | Persistência (testada reiniciando o sistema), validações, mensagens de erro e navegação |
| [05](sprints/sprint-05/README.md) | Módulo 2: acompanhamento de temas | Concluída | Conta com e-mail, temas acompanhados, atualizações por e-mail, regras de negócio e bugs corrigidos |
| [06](sprints/sprint-06/README.md) | Módulo 3 e integração | Concluída | Consulta com IA (RAG), integração entre os módulos e ajustes de interface |
| [07](sprints/sprint-07/README.md) | Dashboard e relatórios | Concluída | Dashboard, relatórios, pesquisas, filtros, CSV e histórico de operações |
| [08](sprints/sprint-08/README.md) | Consolidação | Em andamento | Matriz de permissões por perfil e situação dos requisitos |
| [09](sprints/sprint-09/README.md) | Verificação e documentação | Concluída | 88 testes automatizados, 26 casos de teste no sistema real, 6 bugs corrigidos |

## Os três módulos do sistema

| Módulo | Para quem | O que faz |
| --- | --- | --- |
| **1. Gestão da base de conhecimento** | Equipe (administrador e curador) | Mantém os trechos da cartilha que a IA usa |
| **2. Acompanhamento de temas** | Pessoas com conta | Conta com e-mail, temas acompanhados e atualizações enviadas pela equipe por e-mail |
| **3. Consulta inteligente** | Qualquer pessoa | Pergunta → busca na cartilha → resposta da IA com fontes → "Saber mais" por e-mail |

## Outros documentos

| Documento | Conteúdo |
| --- | --- |
| [Guia de configuração](configuracao.md) | Como configurar o Supabase, o Google Gemini e o envio de e-mails pelo Gmail (passo a passo) |
| [Guia de publicação](publicacao.md) | Como publicar o Oráculo na internet de graça pela Vercel (passo a passo) |
| [Avaliação das respostas da IA](avaliacao-ia.md) | Perguntas de referência feitas à IA real e se cada resposta atendeu aos critérios (PB12) |
| [Paralelismo e concorrência](paralelismo.md) | Onde o sistema executa tarefas em paralelo, com testes e medição (para a conversa com o orientador) |
| [Registro de decisões](decisoes.md) | O que foi pensado, testado e trocado durante o projeto (como o WhatsApp) e por quê |
| [Relatório de entrega (PDF)](entrega/) | Documento único com as Sprints 01 a 09, no estilo do relatório da Sprint 01 |
| [Histórico de versões](../CHANGELOG.md) | Cada versão enviada ao GitHub: data, objetivo, o que mudou e como agrega |
| [Scripts do banco](../supabase/) | Estrutura do banco, na ordem em que deve ser executada (001 a 005) |
| [Evidências](evidencias/) | Prints e arquivos exportados nos testes com o sistema real |
| [Ferramentas](ferramentas/) | Roteiro automatizado que testa as telas e gera as evidências |
| [README do projeto](../README.md) | Visão geral, tecnologias e como executar |
