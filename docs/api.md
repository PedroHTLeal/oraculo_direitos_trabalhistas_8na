# Documentação da API

**Versão:** 1.0.0-rc.3 (Release Candidate) · **Base:** `https://oraculo-direitos-trabalhistas-8na.vercel.app` · **Documentação interativa (Swagger):** [https://oraculo-direitos-trabalhistas-8na.vercel.app/api/docs](https://oraculo-direitos-trabalhistas-8na.vercel.app/api/docs)

Gerada a partir da especificação OpenAPI do backend por [`docs/ferramentas/gerar_doc_api.py`](ferramentas/gerar_doc_api.py). No Swagger é possível testar cada rota pelo navegador (botão *Authorize* para usar o token).

API do **Oráculo dos Direitos Trabalhistas**: consulta à Cartilha de Direitos e Obrigações
no Trabalho do TRT4 com IA (RAG), envio de conteúdo complementar por e-mail, acompanhamento
de temas e painel da equipe.

**Autenticação:** as rotas restritas usam o token devolvido por `POST /api/auth/login`, enviado no
cabeçalho `Authorization: Bearer <token>`. A sessão vale por 8 horas.

**Erros:** todas as respostas de erro trazem `detail` com uma frase pronta para mostrar ao usuário;
os erros de validação (422) trazem também `erros`, uma mensagem por campo.

## Resumo das rotas

| Método | Rota | O que faz | Acesso |
| --- | --- | --- | --- |
| `GET` | `/api/sugestoes` | Temas e perguntas sugeridos | Aberta (sem login) |
| `POST` | `/api/perguntas` | Fazer uma pergunta | Aberta (sem login) |
| `POST` | `/api/saiba-mais` | Pedir mais conteúdo por e-mail | Aberta (sem login) |
| `GET` | `/api/saiba-mais/{solicitacao_id}` | Situação do pedido de e-mail | Aberta (sem login) |
| `POST` | `/api/auth/cadastro` | Criar conta | Aberta (sem login) |
| `POST` | `/api/auth/login` | Entrar | Aberta (sem login) |
| `POST` | `/api/auth/sair` | Sair | Qualquer pessoa logada |
| `GET` | `/api/auth/eu` | Conta atual | Qualquer pessoa logada |
| `GET` | `/api/usuarios` | Listar usuários | Administrador |
| `POST` | `/api/usuarios` | Cadastrar usuário | Administrador |
| `PUT` | `/api/usuarios/{usuario_id}` | Alterar usuário | Administrador |
| `DELETE` | `/api/usuarios/{usuario_id}` | Excluir usuário | Administrador |
| `GET` | `/api/temas` | Listar temas da cartilha | Aberta (sem login) |
| `GET` | `/api/base/trechos` | Listar trechos | Curador ou administrador |
| `POST` | `/api/base/trechos` | Incluir trecho | Curador ou administrador |
| `GET` | `/api/base/trechos/{trecho_id}` | Ver trecho | Curador ou administrador |
| `PUT` | `/api/base/trechos/{trecho_id}` | Alterar trecho | Curador ou administrador |
| `DELETE` | `/api/base/trechos/{trecho_id}` | Excluir trecho | Curador ou administrador |
| `GET` | `/api/base/perguntas` | Perguntas recentes | Curador ou administrador |
| `GET` | `/api/sinonimos` | Listar sinônimos | Curador ou administrador |
| `POST` | `/api/sinonimos` | Incluir sinônimo | Curador ou administrador |
| `PUT` | `/api/sinonimos/{termo}` | Alterar sinônimo | Curador ou administrador |
| `DELETE` | `/api/sinonimos/{termo}` | Excluir sinônimo | Curador ou administrador |
| `GET` | `/api/materiais` | Listar sites e vídeos | Curador ou administrador |
| `POST` | `/api/materiais` | Incluir site ou vídeo | Curador ou administrador |
| `PUT` | `/api/materiais/{material_id}` | Alterar site ou vídeo | Curador ou administrador |
| `DELETE` | `/api/materiais/{material_id}` | Excluir site ou vídeo | Curador ou administrador |
| `GET` | `/api/inscricoes` | Meus temas | Qualquer pessoa logada |
| `POST` | `/api/inscricoes` | Acompanhar tema | Qualquer pessoa logada |
| `DELETE` | `/api/inscricoes/{inscricao_id}` | Deixar de acompanhar | Qualquer pessoa logada |
| `GET` | `/api/atualizacoes` | Listar atualizações | Curador ou administrador |
| `POST` | `/api/atualizacoes` | Publicar novidade | Curador ou administrador |
| `POST` | `/api/atualizacoes/{atualizacao_id}/reenviar` | Reenviar falhas | Curador ou administrador |
| `DELETE` | `/api/atualizacoes/{atualizacao_id}` | Excluir atualização | Curador ou administrador |
| `GET` | `/api/minhas-atualizacoes` | Novidades dos meus temas | Qualquer pessoa logada |
| `GET` | `/api/painel/indicadores` | Indicadores do dashboard | Curador ou administrador |
| `GET` | `/api/relatorios/perguntas` | Relatório de perguntas | Curador ou administrador |
| `GET` | `/api/relatorios/historico` | Histórico de operações | Administrador |
| `GET` | `/api/saude` | Situação do serviço | Aberta (sem login) |

## Consulta

Perguntas sobre direitos trabalhistas e o "Saber mais" por e-mail. Abertas, sem login.

### Temas e perguntas sugeridos

`GET /api/sugestoes` · **Acesso:** Aberta (sem login)

Perguntas exibidas na página inicial (RF02).

**Respostas:** `200` OK

### Fazer uma pergunta

`POST /api/perguntas` · **Acesso:** Aberta (sem login)

Busca os trechos da cartilha mais relevantes e gera a resposta com a IA usando só esses trechos (RAG). Devolve a resposta, as fontes e se a cartilha trata do assunto (RF04 a RF09).

**Corpo (JSON, Pergunta)**

| Campo | Tipo | Obrigatório | Regras |
| --- | --- | --- | --- |
| `texto` | texto | Sim | mín. 3 caracteres; máx. 500 caracteres |

**Respostas:** `200` OK: `Resposta`

### Pedir mais conteúdo por e-mail

`POST /api/saiba-mais` · **Acesso:** Aberta (sem login)

Envia ao e-mail informado a resposta, sites e vídeos sobre o assunto. Exige a autorização (LGPD); até 5 pedidos por e-mail a cada hora (RF10, RF11).

**Corpo (JSON, PedidoSaibaMais)**

| Campo | Tipo | Obrigatório | Regras |
| --- | --- | --- | --- |
| `pergunta_id` | texto | Sim | — |
| `nome` | texto | Sim | mín. 2 caracteres; máx. 100 caracteres |
| `email` | e-mail | Sim | — |
| `consentimento` | verdadeiro/falso | Sim | — |

**Respostas:** `202` Aceito (envio em andamento): `SituacaoPedido`

### Situação do pedido de e-mail

`GET /api/saiba-mais/{solicitacao_id}` · **Acesso:** Aberta (sem login)

pendente, enviado ou erro.

**Parâmetros**

| Nome | Onde | Tipo | Obrigatório | Regras |
| --- | --- | --- | --- | --- |
| `solicitacao_id` | rota | texto | Sim | — |

**Respostas:** `200` OK: `SituacaoPedido`

## Autenticação

Cadastro, login e logout.

### Criar conta

`POST /api/auth/cadastro` · **Acesso:** Aberta (sem login)

Cria uma conta de usuário comum e já abre a sessão.

**Corpo (JSON, Cadastro)**

| Campo | Tipo | Obrigatório | Regras |
| --- | --- | --- | --- |
| `nome` | texto | Sim | mín. 2 caracteres; máx. 100 caracteres |
| `email` | e-mail | Sim | — |
| `senha` | texto | Sim | mín. 8 caracteres; máx. 128 caracteres |
| `consentimento` | verdadeiro/falso | Sim | — |

**Respostas:** `201` Criado: `Sessao`

### Entrar

`POST /api/auth/login` · **Acesso:** Aberta (sem login)

Devolve o token de acesso e os dados da conta.

**Corpo (JSON, Login)**

| Campo | Tipo | Obrigatório | Regras |
| --- | --- | --- | --- |
| `email` | e-mail | Sim | — |
| `senha` | texto | Sim | mín. 1 caracteres; máx. 128 caracteres |

**Respostas:** `200` OK: `Sessao`

### Sair

`POST /api/auth/sair` · **Acesso:** Qualquer pessoa logada

Encerra a sessão do token enviado.

**Respostas:** `204` Sem conteúdo

### Conta atual

`GET /api/auth/eu` · **Acesso:** Qualquer pessoa logada

Dados da pessoa dona do token.

**Respostas:** `200` OK: `Usuario`

## Usuários

Gestão de contas e perfis. Só administradores.

### Listar usuários

`GET /api/usuarios` · **Acesso:** Administrador

Todas as contas, com perfil e situação.

**Respostas:** `200` OK: lista de `Usuario`

### Cadastrar usuário

`POST /api/usuarios` · **Acesso:** Administrador

Cria uma conta com o perfil escolhido.

**Corpo (JSON, NovoUsuario)**

| Campo | Tipo | Obrigatório | Regras |
| --- | --- | --- | --- |
| `nome` | texto | Sim | mín. 2 caracteres; máx. 100 caracteres |
| `email` | e-mail | Sim | — |
| `senha` | texto | Sim | mín. 8 caracteres; máx. 128 caracteres |
| `perfil` | `administrador` / `curador` / `usuario` | Não | padrão: `usuario` |

**Respostas:** `201` Criado: `Usuario`

### Alterar usuário

`PUT /api/usuarios/{usuario_id}` · **Acesso:** Administrador

Altera nome, e-mail, perfil, situação ou senha. O sistema nunca fica sem um administrador ativo.

**Parâmetros**

| Nome | Onde | Tipo | Obrigatório | Regras |
| --- | --- | --- | --- | --- |
| `usuario_id` | rota | texto | Sim | — |

**Corpo (JSON, AlteracaoUsuario)**

| Campo | Tipo | Obrigatório | Regras |
| --- | --- | --- | --- |
| `nome` | texto (opcional) | Não | mín. 2 caracteres; máx. 100 caracteres |
| `email` | e-mail (opcional) | Não | — |
| `perfil` | `administrador` / `curador` / `usuario` (opcional) | Não | — |
| `ativo` | verdadeiro/falso (opcional) | Não | — |
| `senha` | texto (opcional) | Não | mín. 8 caracteres; máx. 128 caracteres |

**Respostas:** `200` OK: `Usuario`

### Excluir usuário

`DELETE /api/usuarios/{usuario_id}` · **Acesso:** Administrador

Ninguém pode excluir a própria conta.

**Parâmetros**

| Nome | Onde | Tipo | Obrigatório | Regras |
| --- | --- | --- | --- | --- |
| `usuario_id` | rota | texto | Sim | — |

**Respostas:** `204` Sem conteúdo

## Base de conhecimento

Trechos da cartilha usados pela IA e auditoria das perguntas.

### Listar temas da cartilha

`GET /api/temas` · **Acesso:** Aberta (sem login)

As 25 páginas da cartilha do TRT4.

**Respostas:** `200` OK: lista de `Tema`

### Listar trechos

`GET /api/base/trechos` · **Acesso:** Curador ou administrador

Com filtro por tema, busca no texto e paginação.

**Parâmetros**

| Nome | Onde | Tipo | Obrigatório | Regras |
| --- | --- | --- | --- | --- |
| `tema_id` | consulta (?) | número inteiro (opcional) | Não | — |
| `busca` | consulta (?) | texto (opcional) | Não | máx. 100 caracteres |
| `pagina` | consulta (?) | número inteiro | Não | mín. 1; padrão: `1` |
| `por_pagina` | consulta (?) | número inteiro | Não | mín. 1; máx. 100; padrão: `20` |

**Respostas:** `200` OK: `PaginaTrechos`

### Incluir trecho

`POST /api/base/trechos` · **Acesso:** Curador ou administrador

Novo trecho, já usado pela IA nas respostas (UC07).

**Corpo (JSON, DadosTrecho)**

| Campo | Tipo | Obrigatório | Regras |
| --- | --- | --- | --- |
| `tema_id` | número inteiro | Sim | — |
| `secao` | texto | Sim | mín. 2 caracteres; máx. 200 caracteres |
| `texto` | texto | Sim | mín. 10 caracteres; máx. 5000 caracteres |

**Respostas:** `201` Criado: `Trecho`

### Ver trecho

`GET /api/base/trechos/{trecho_id}` · **Acesso:** Curador ou administrador

Um trecho da cartilha.

**Parâmetros**

| Nome | Onde | Tipo | Obrigatório | Regras |
| --- | --- | --- | --- | --- |
| `trecho_id` | rota | número inteiro | Sim | — |

**Respostas:** `200` OK: `Trecho`

### Alterar trecho

`PUT /api/base/trechos/{trecho_id}` · **Acesso:** Curador ou administrador

Altera tema, subtítulo ou texto.

**Parâmetros**

| Nome | Onde | Tipo | Obrigatório | Regras |
| --- | --- | --- | --- | --- |
| `trecho_id` | rota | número inteiro | Sim | — |

**Corpo (JSON, DadosTrecho)**

| Campo | Tipo | Obrigatório | Regras |
| --- | --- | --- | --- |
| `tema_id` | número inteiro | Sim | — |
| `secao` | texto | Sim | mín. 2 caracteres; máx. 200 caracteres |
| `texto` | texto | Sim | mín. 10 caracteres; máx. 5000 caracteres |

**Respostas:** `200` OK: `Trecho`

### Excluir trecho

`DELETE /api/base/trechos/{trecho_id}` · **Acesso:** Curador ou administrador

Remove o trecho da base.

**Parâmetros**

| Nome | Onde | Tipo | Obrigatório | Regras |
| --- | --- | --- | --- | --- |
| `trecho_id` | rota | número inteiro | Sim | — |

**Respostas:** `204` Sem conteúdo

### Perguntas recentes

`GET /api/base/perguntas` · **Acesso:** Curador ou administrador

Auditoria das perguntas, sem dados pessoais (UC08).

**Respostas:** `200` OK: lista de `PerguntaRegistrada`

## Conteúdo complementar

Sinônimos da busca e sites e vídeos enviados no "Saber mais".

### Listar sinônimos

`GET /api/sinonimos` · **Acesso:** Curador ou administrador

Palavras do dia a dia e os termos da cartilha que a busca usa no lugar.

**Respostas:** `200` OK: lista de `Sinonimo`

### Incluir sinônimo

`POST /api/sinonimos` · **Acesso:** Curador ou administrador

Grava sem acentos e em minúsculas.

**Corpo (JSON, DadosSinonimo)**

| Campo | Tipo | Obrigatório | Regras |
| --- | --- | --- | --- |
| `termo` | texto | Sim | mín. 2 caracteres; máx. 60 caracteres |
| `equivalentes` | texto | Sim | mín. 2 caracteres; máx. 200 caracteres |

**Respostas:** `201` Criado: `Sinonimo`

### Alterar sinônimo

`PUT /api/sinonimos/{termo}` · **Acesso:** Curador ou administrador

Altera a palavra ou os termos equivalentes.

**Parâmetros**

| Nome | Onde | Tipo | Obrigatório | Regras |
| --- | --- | --- | --- | --- |
| `termo` | rota | texto | Sim | — |

**Corpo (JSON, DadosSinonimo)**

| Campo | Tipo | Obrigatório | Regras |
| --- | --- | --- | --- |
| `termo` | texto | Sim | mín. 2 caracteres; máx. 60 caracteres |
| `equivalentes` | texto | Sim | mín. 2 caracteres; máx. 200 caracteres |

**Respostas:** `200` OK: `Sinonimo`

### Excluir sinônimo

`DELETE /api/sinonimos/{termo}` · **Acesso:** Curador ou administrador

A busca deixa de traduzir a palavra.

**Parâmetros**

| Nome | Onde | Tipo | Obrigatório | Regras |
| --- | --- | --- | --- | --- |
| `termo` | rota | texto | Sim | — |

**Respostas:** `204` Sem conteúdo

### Listar sites e vídeos

`GET /api/materiais` · **Acesso:** Curador ou administrador

Links do "Saber mais", por assunto.

**Respostas:** `200` OK: lista de `Material`

### Incluir site ou vídeo

`POST /api/materiais` · **Acesso:** Curador ou administrador

Vídeos só do YouTube; o mesmo link não se repete no assunto.

**Corpo (JSON, DadosMaterial)**

| Campo | Tipo | Obrigatório | Regras |
| --- | --- | --- | --- |
| `tema_id` | número inteiro | Sim | — |
| `assunto` | texto | Sim | mín. 2 caracteres; máx. 80 caracteres |
| `palavras_chave` | lista de texto | Sim | — |
| `tipo` | `site` / `video` | Sim | — |
| `titulo` | texto | Sim | mín. 3 caracteres; máx. 200 caracteres |
| `url` | texto | Sim | máx. 500 caracteres; começa com http:// ou https:// |
| `ordem` | número inteiro | Não | mín. 1.0; máx. 9.0; padrão: `1` |

**Respostas:** `201` Criado: `Material`

### Alterar site ou vídeo

`PUT /api/materiais/{material_id}` · **Acesso:** Curador ou administrador

Altera os dados do link.

**Parâmetros**

| Nome | Onde | Tipo | Obrigatório | Regras |
| --- | --- | --- | --- | --- |
| `material_id` | rota | número inteiro | Sim | — |

**Corpo (JSON, DadosMaterial)**

| Campo | Tipo | Obrigatório | Regras |
| --- | --- | --- | --- |
| `tema_id` | número inteiro | Sim | — |
| `assunto` | texto | Sim | mín. 2 caracteres; máx. 80 caracteres |
| `palavras_chave` | lista de texto | Sim | — |
| `tipo` | `site` / `video` | Sim | — |
| `titulo` | texto | Sim | mín. 3 caracteres; máx. 200 caracteres |
| `url` | texto | Sim | máx. 500 caracteres; começa com http:// ou https:// |
| `ordem` | número inteiro | Não | mín. 1.0; máx. 9.0; padrão: `1` |

**Respostas:** `200` OK: `Material`

### Excluir site ou vídeo

`DELETE /api/materiais/{material_id}` · **Acesso:** Curador ou administrador

O link deixa de ser enviado.

**Parâmetros**

| Nome | Onde | Tipo | Obrigatório | Regras |
| --- | --- | --- | --- | --- |
| `material_id` | rota | número inteiro | Sim | — |

**Respostas:** `204` Sem conteúdo

## Acompanhamento de temas

Temas que cada usuário acompanha.

### Meus temas

`GET /api/inscricoes` · **Acesso:** Qualquer pessoa logada

Temas que a pessoa logada acompanha.

**Respostas:** `200` OK: lista de `Inscricao`

### Acompanhar tema

`POST /api/inscricoes` · **Acesso:** Qualquer pessoa logada

As novidades do tema passam a chegar no e-mail da conta (RF12).

**Corpo (JSON, NovaInscricao)**

| Campo | Tipo | Obrigatório | Regras |
| --- | --- | --- | --- |
| `tema_id` | número inteiro | Sim | — |

**Respostas:** `201` Criado: `Inscricao`

### Deixar de acompanhar

`DELETE /api/inscricoes/{inscricao_id}` · **Acesso:** Qualquer pessoa logada

Só as inscrições da própria conta.

**Parâmetros**

| Nome | Onde | Tipo | Obrigatório | Regras |
| --- | --- | --- | --- | --- |
| `inscricao_id` | rota | texto | Sim | — |

**Respostas:** `204` Sem conteúdo

## Atualizações

Novidades dos temas, enviadas por e-mail a quem acompanha.

### Listar atualizações

`GET /api/atualizacoes` · **Acesso:** Curador ou administrador

Novidades publicadas, com a situação dos envios.

**Parâmetros**

| Nome | Onde | Tipo | Obrigatório | Regras |
| --- | --- | --- | --- | --- |
| `tema_id` | consulta (?) | número inteiro (opcional) | Não | — |

**Respostas:** `200` OK: lista de `Atualizacao`

### Publicar novidade

`POST /api/atualizacoes` · **Acesso:** Curador ou administrador

Salva a novidade e envia por e-mail, em paralelo, a quem acompanha o tema (RF13).

**Corpo (JSON, NovaAtualizacao)**

| Campo | Tipo | Obrigatório | Regras |
| --- | --- | --- | --- |
| `tema_id` | número inteiro | Sim | — |
| `titulo` | texto | Sim | mín. 5 caracteres; máx. 120 caracteres |
| `conteudo` | texto | Sim | mín. 20 caracteres; máx. 1000 caracteres |
| `url` | texto (opcional) | Não | máx. 500 caracteres; começa com http:// ou https:// |

**Respostas:** `201` Criado: `Atualizacao`

### Reenviar falhas

`POST /api/atualizacoes/{atualizacao_id}/reenviar` · **Acesso:** Curador ou administrador

Envia de novo só os e-mails que deram erro.

**Parâmetros**

| Nome | Onde | Tipo | Obrigatório | Regras |
| --- | --- | --- | --- | --- |
| `atualizacao_id` | rota | número inteiro | Sim | — |

**Respostas:** `200` OK: `Atualizacao`

### Excluir atualização

`DELETE /api/atualizacoes/{atualizacao_id}` · **Acesso:** Curador ou administrador

O curador só exclui as próprias publicações; o administrador, qualquer uma.

**Parâmetros**

| Nome | Onde | Tipo | Obrigatório | Regras |
| --- | --- | --- | --- | --- |
| `atualizacao_id` | rota | número inteiro | Sim | — |

**Respostas:** `204` Sem conteúdo

### Novidades dos meus temas

`GET /api/minhas-atualizacoes` · **Acesso:** Qualquer pessoa logada

Últimas novidades dos temas acompanhados.

**Respostas:** `200` OK: lista de `Atualizacao`

## Dashboard e relatórios

Indicadores, relatórios com filtros, exportação em CSV e histórico.

### Indicadores do dashboard

`GET /api/painel/indicadores` · **Acesso:** Curador ou administrador

Período de 7, 30, 90 ou 365 dias.

**Parâmetros**

| Nome | Onde | Tipo | Obrigatório | Regras |
| --- | --- | --- | --- | --- |
| `dias` | consulta (?) | número inteiro | Não | padrão: `30` |

**Respostas:** `200` OK

### Relatório de perguntas

`GET /api/relatorios/perguntas` · **Acesso:** Curador ou administrador

Filtros por período, tema, resultado e texto; `formato=csv` exporta.

**Parâmetros**

| Nome | Onde | Tipo | Obrigatório | Regras |
| --- | --- | --- | --- | --- |
| `inicio` | consulta (?) | texto (opcional) | Não | — |
| `fim` | consulta (?) | texto (opcional) | Não | — |
| `resultado` | consulta (?) | `respondida` / `sem_resposta` (opcional) | Não | — |
| `tema_id` | consulta (?) | número inteiro (opcional) | Não | — |
| `busca` | consulta (?) | texto (opcional) | Não | máx. 100 caracteres |
| `formato` | consulta (?) | `json` / `csv` | Não | padrão: `json` |

**Respostas:** `200` OK

### Histórico de operações

`GET /api/relatorios/historico` · **Acesso:** Administrador

Quem fez o quê e quando; filtros por período, ação, área e texto; `formato=csv` exporta.

**Parâmetros**

| Nome | Onde | Tipo | Obrigatório | Regras |
| --- | --- | --- | --- | --- |
| `inicio` | consulta (?) | texto (opcional) | Não | — |
| `fim` | consulta (?) | texto (opcional) | Não | — |
| `acao` | consulta (?) | texto (opcional) | Não | — |
| `entidade` | consulta (?) | texto (opcional) | Não | — |
| `busca` | consulta (?) | texto (opcional) | Não | máx. 100 caracteres |
| `formato` | consulta (?) | `json` / `csv` | Não | padrão: `json` |

**Respostas:** `200` OK

## Outros

Situação do serviço.

### Situação do serviço

`GET /api/saude` · **Acesso:** Aberta (sem login)

Confere se a API está no ar.

**Respostas:** `200` OK

## Exemplos de uso

Fazer uma pergunta (aberta, sem login):

```bash
curl -X POST https://oraculo-direitos-trabalhistas-8na.vercel.app/api/perguntas \
  -H "Content-Type: application/json" \
  -d '{"texto": "Quantos dias de férias eu tenho direito?"}'
```

```json
{
  "id": "5f0c…",
  "pergunta": "Quantos dias de férias eu tenho direito?",
  "resposta": "Você tem direito a 30 dias de férias por ano…",
  "encontrou": true,
  "fontes": [{"titulo": "Férias · Pagamento das férias", "trecho": "…", "url": "https://www.trt4.jus.br/portais/trt4/ferias"}]
}
```

Pedir mais conteúdo por e-mail:

```bash
curl -X POST https://oraculo-direitos-trabalhistas-8na.vercel.app/api/saiba-mais \
  -H "Content-Type: application/json" \
  -d '{"pergunta_id": "5f0c…", "nome": "Maria", "email": "maria@exemplo.com", "consentimento": true}'
```

Entrar e usar o token em uma rota da equipe:

```bash
curl -X POST https://oraculo-direitos-trabalhistas-8na.vercel.app/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "curador@exemplo.com", "senha": "sua-senha"}'
# resposta: {"token": "…", "usuario": {…}}

curl https://oraculo-direitos-trabalhistas-8na.vercel.app/api/base/trechos?tema_id=7 -H "Authorization: Bearer <token>"
```

Erro de validação (422):

```json
{"detail": "Preencha o campo e-mail.", "erros": ["Preencha o campo e-mail."]}
```
