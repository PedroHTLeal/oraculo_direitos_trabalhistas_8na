# Oráculo dos Direitos Trabalhistas

Plataforma que recebe dúvidas em linguagem natural e apresenta respostas simples e acessíveis sobre direitos e obrigações trabalhistas, sempre indicando a fonte utilizada: a *Cartilha de Direitos e Obrigações no Trabalho* do Tribunal Regional do Trabalho da 4ª Região (TRT4).

Projeto da turma **8NA** de Ciência da Computação, desenvolvido para as disciplinas de Fábrica de Software, Tópicos Avançados e DevOps Tools.

| | |
| --- | --- |
| **Versão** | 1.0.0-rc.3 (Release Candidate) |
| **Sistema publicado** | https://oraculo-direitos-trabalhistas-8na.vercel.app |
| **Documentação da API** | [docs/api.md](docs/api.md) e Swagger em https://oraculo-direitos-trabalhistas-8na.vercel.app/api/docs |
| **Documentação por Sprint** | [docs/](docs/README.md), com o relatório único em PDF em [docs/entrega/](docs/entrega/) |

## Objetivo

Facilitar o acesso à informação sobre direitos e obrigações trabalhistas por meio de uma plataforma com Inteligência Artificial que responde dúvidas em linguagem acessível, usando só fontes confiáveis.

**Problema:** termos jurídicos, excesso de informação e dificuldade de achar conteúdo confiável afastam as pessoas dos próprios direitos. **Público-alvo:** trabalhadores em geral, com atenção a informais e de aplicativos, domésticos, pessoas com pouca familiaridade com termos jurídicos ou ferramentas digitais, jovens, estudantes e estagiários.

O sistema usa **RAG (Retrieval-Augmented Generation)**: antes de gerar a resposta, busca os trechos relevantes da cartilha, e a IA escreve **somente** com base neles. Quando a cartilha não trata do assunto, o sistema avisa em vez de inventar.

## Como funciona

| Módulo | Para quem | O que faz |
| --- | --- | --- |
| **1. Gestão da base de conhecimento** | Equipe (administrador e curador) | Trechos da cartilha, sinônimos da busca, sites e vídeos do "Saber mais", dashboard, relatórios e histórico |
| **2. Acompanhamento de temas** | Pessoas com conta | Escolher temas e receber por e-mail as novidades publicadas pela equipe |
| **3. Consulta inteligente** | Qualquer pessoa, sem login | Pergunta → busca na cartilha → resposta da IA com fontes → "Saber mais" por e-mail |

Fluxo da consulta: a pessoa faz a pergunta; o backend busca os trechos mais relevantes no Supabase (dando mais peso às palavras raras); a IA escreve a resposta usando só esses trechos; a tela mostra a resposta com as fontes e o link para a cartilha; em "Quer saber mais sobre o assunto? Sim", a pessoa informa nome e e-mail e recebe a resposta com sites e vídeos escolhidos pela equipe.

## Tecnologias

| Camada | Tecnologia |
| --- | --- |
| Backend | Python 3.12, [FastAPI](https://fastapi.tiangolo.com/) (API documentada com OpenAPI/Swagger) |
| Frontend | React 18 com [Vite](https://vite.dev/) |
| Banco de dados | [Supabase](https://supabase.com/) (PostgreSQL), busca textual em português sem acentos |
| Inteligência Artificial | [Google Gemini](https://ai.google.dev/) (plano gratuito), com uma fila de 3 modelos reserva quando o principal está sobrecarregado ou sem cota |
| E-mail | Gmail (SMTP) com senha de app |
| Paralelismo | Threads em Python no envio das novidades e no dashboard ([detalhes](docs/paralelismo.md)) |
| Testes e qualidade | pytest (103 testes), ESLint, roteiro de testes no navegador com Playwright |
| Integração contínua | GitHub Actions: testes e compilação a cada envio ao GitHub, e uma rotina a cada 2 dias que mantém o banco ativo |
| Publicação | [Vercel](https://vercel.com/) (plano gratuito), atualizada a cada envio ao `main` |

## Requisitos para executar

- **Python 3.12** ou mais novo e **Node.js 20** ou mais novo.
- Contas gratuitas no **Supabase** (banco) e no **Google AI Studio** (chave do Gemini).
- Uma conta do **Gmail** com verificação em duas etapas, para gerar a senha de app dos e-mails.
- Git, para baixar o repositório.

## Instalação e configuração

1. Baixe o projeto:

   ```bash
   git clone https://github.com/PedroHTLeal/oraculo_direitos_trabalhistas_8na.git
   ```

2. Copie o modelo das chaves e preencha (o arquivo `.env` nunca vai para o GitHub):

   ```bash
   cp backend/.env.example backend/.env
   ```

   | Variável | De onde vem |
   | --- | --- |
   | `SUPABASE_URL` e `SUPABASE_SERVICE_ROLE_KEY` | Supabase › Project Settings › API |
   | `GEMINI_API_KEY` | https://aistudio.google.com › Get API key |
   | `EMAIL_REMETENTE` e `EMAIL_SENHA_APP` | O Gmail que envia os e-mails e a senha de app dele |

O passo a passo de cada conta, com a solução dos problemas mais comuns, está no [guia de configuração](docs/configuracao.md).

## Banco de dados

1. Crie um projeto no Supabase (região São Paulo).
2. No **SQL Editor**, execute em ordem os scripts da pasta [`supabase/`](supabase/), do `001` ao `008`.
3. Carregue a cartilha do TRT4 (25 temas e 217 trechos), na pasta `backend/` com o ambiente virtual ativo:

   ```bash
   python scripts/carregar_cartilha.py
   ```

4. Crie o primeiro administrador:

   ```bash
   python scripts/criar_administrador.py
   ```

A estrutura final (tabelas, chaves, regras e segurança) está descrita em [docs/banco-de-dados.md](docs/banco-de-dados.md), e os diagramas (MER e modelo relacional), na [Sprint 02](docs/sprints/sprint-02/diagramas.md). No plano gratuito, o Supabase pausa o banco depois de 7 dias sem uso; uma rotina do GitHub Actions usa o banco a cada 2 dias para evitar isso. Se ele pausar, abra o projeto no Supabase e clique em **Restore project**.

## Como executar

**Sistema completo no computador (Windows):**

```bash
iniciar.bat
```

O script cria o ambiente do Python, instala as dependências, compila o frontend e abre o sistema em http://localhost:8000. No Linux ou macOS, use `./iniciar.sh`.

**Desenvolvimento** (recarrega a cada alteração): backend em `backend/` com `uvicorn app.main:app --reload --port 8000` e frontend em `frontend/` com `npm run dev` (http://localhost:5173).

**Testes automatizados** (em `backend/`):

```bash
pytest
```

**Publicar na internet:** veja o [guia de publicação na Vercel](docs/publicacao.md). O sistema já publicado fica em https://oraculo-direitos-trabalhistas-8na.vercel.app; a equipe entra pelo endereço `/entrar`.

## Estrutura do projeto

```
backend/          API em Python (FastAPI)
  app/            rotas, regras de negócio, IA, busca, e-mail e acesso ao banco
  tests/          103 testes automatizados (pytest)
  scripts/        carregar a cartilha, criar o administrador e contas de demonstração
frontend/         Interface em React (consulta pública e painel da equipe)
supabase/         Estrutura do banco, em scripts numerados (001 a 008)
api/              Entrada do backend na Vercel (com vercel.json na raiz)
docs/             Documentação: Sprints, API, banco, configuração, publicação e ferramentas
.github/          GitHub Actions: testes a cada envio e rotina que mantém o banco ativo
iniciar.bat       Executa o sistema completo no Windows (iniciar.sh no Linux/macOS)
```

O histórico de cada versão está em [CHANGELOG.md](CHANGELOG.md): cada ajuste é um commit no `main`, com data, objetivo, o que foi feito e como agrega ao projeto.

## Equipe

**Kaleido Void Studios** · Ciência da Computação, turma 8NA

| Integrante | Matrícula |
| --- | --- |
| Pedro Henrique Tenório Leal | 01591056 |
| Gerson Martinho Mesquita Neto | 01604283 |
