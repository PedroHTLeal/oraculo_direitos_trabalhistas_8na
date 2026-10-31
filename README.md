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

## Estrutura do repositório

```
docs/    Documentação do projeto e relatórios das Sprints
```

As pastas da aplicação (frontend, backend, base de conhecimento) serão criadas quando as tecnologias forem definidas.

## Equipe

**Kaleido Void Studios**

- Pedro Henrique Tenório Leal
