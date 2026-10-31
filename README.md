# Oráculo dos Direitos Trabalhistas

Plataforma que recebe dúvidas dos usuários em linguagem natural e apresenta respostas simples e acessíveis sobre direitos e obrigações trabalhistas, sempre indicando a fonte utilizada.

Projeto da turma **8NA** de Ciência da Computação, desenvolvido para as disciplinas de Fábrica de Software, Tópicos Avançados e DevOps Tools.

## Proposta

O sistema utiliza uma abordagem de **RAG (Retrieval-Augmented Generation)**: antes de gerar uma resposta, busca as informações relevantes em uma base de conhecimento formada por fontes confiáveis. A referência inicial é a *Cartilha de Direitos e Obrigações no Trabalho* do Tribunal Regional do Trabalho da 4ª Região (TRT4).

Cada disciplina tem um enfoque diferente sobre o mesmo projeto:

| Disciplina | Enfoque |
| --- | --- |
| Fábrica de Software | Organização e gestão do desenvolvimento |
| Tópicos Avançados | Inteligência Artificial, RAG, LLM e avaliação das respostas |
| DevOps Tools | Versionamento, integração, testes, automação e entrega |

## Problema

O acesso a informações sobre direitos e obrigações trabalhistas é dificultado pelos termos jurídicos, pela quantidade de informação disponível e pela dificuldade de localizar e interpretar conteúdos confiáveis.

> Como facilitar o acesso e a compreensão de informações sobre direitos e obrigações trabalhistas por meio de uma plataforma digital que permita ao usuário realizar perguntas em linguagem natural e obter respostas baseadas em fontes confiáveis?

## Objetivos

**Objetivo geral:** facilitar o acesso à informação sobre direitos e obrigações trabalhistas por meio de uma plataforma com Inteligência Artificial capaz de responder dúvidas em linguagem acessível, utilizando fontes confiáveis.

**Objetivos específicos:**

- Permitir que o usuário faça perguntas em linguagem natural.
- Facilitar a localização de informações sobre direitos e obrigações trabalhistas.
- Fundamentar as respostas em uma base de conhecimento confiável.
- Aplicar RAG para recuperar informações relevantes antes de gerar a resposta.
- Apresentar as respostas em linguagem simples e compreensível.
- Informar a fonte de cada resposta e permitir a consulta ao conteúdo original.
- Evitar que a IA responda sem informações suficientes na base de conhecimento.
- Permitir a solicitação de conteúdos complementares pelo WhatsApp.
- Permitir que o usuário escolha temas para acompanhar e receber atualizações.

## Público-alvo

Trabalhadores que desejam se informar sobre seus direitos e obrigações, com atenção especial para:

- trabalhadores informais e de aplicativos;
- trabalhadores domésticos;
- pessoas com pouca familiaridade com termos jurídicos ou ferramentas digitais;
- jovens no primeiro contato com o mercado de trabalho, incluindo estudantes e estagiários.

A interface deve priorizar simplicidade e clareza, permitindo uma consulta sem conhecimentos técnicos ou jurídicos.

## Tecnologias

- **Backend:** Python 3.12 com [FastAPI](https://fastapi.tiangolo.com/), testes com pytest
- **Frontend:** React com [Vite](https://vite.dev/)
- **Banco de dados:** [Supabase](https://supabase.com/) (PostgreSQL), com busca textual em português
- **Inteligência Artificial:** [Google Gemini](https://ai.google.dev/) (plano gratuito), para gerar respostas e pesquisar materiais complementares no Google
- **WhatsApp:** [Twilio](https://www.twilio.com/) (Sandbox)

## Como funciona

1. O usuário faz uma pergunta.
2. O backend busca no Supabase os trechos mais relevantes da cartilha do TRT4.
3. A IA escreve uma resposta simples usando **somente** esses trechos e indica quais usou como fonte.
4. Se o usuário pedir para saber mais, informa o WhatsApp; a IA pesquisa 2 sites e 2 vídeos do YouTube sobre o assunto e a Twilio envia tudo para o celular dele.

## Estrutura do repositório

```
backend/    API em Python (FastAPI), scripts e dados da cartilha
frontend/   Interface web em React
supabase/   Estrutura do banco de dados (SQL)
docs/       Documentação do projeto e relatórios das Sprints
```

O histórico de cada versão enviada ao GitHub está em [CHANGELOG.md](CHANGELOG.md).

## Como executar

Pré-requisitos: Python 3.12+ e Node.js 20+, além das contas gratuitas no Supabase, no Google AI Studio (Gemini) e na Twilio. O passo a passo para criá-las e preencher o `backend/.env` está em [docs/configuracao.md](docs/configuracao.md).

**Backend** (em `backend/`):

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows (no Linux/macOS: source .venv/bin/activate)
pip install -r requirements-dev.txt
uvicorn app.main:app --reload --port 8000
```

Testes: `pytest`

**Frontend** (em `frontend/`, com o backend rodando):

```bash
npm install
npm run dev
```

Acesse http://localhost:5173. Em desenvolvimento, as chamadas para `/api` são encaminhadas ao backend na porta 8000.

## Equipe

**Kaleido Void Studios**

- Pedro Henrique Tenório Leal
