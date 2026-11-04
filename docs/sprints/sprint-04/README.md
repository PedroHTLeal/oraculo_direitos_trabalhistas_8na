# Sprint 04 — Módulo 1: gestão da base de conhecimento

**Situação:** Concluída e testada com o banco real · [← Voltar ao índice](../../README.md)

## O que a Sprint pediu

Primeiro módulo totalmente funcional, com persistência de dados, validações, mensagens de erro claras, navegação entre telas e commits organizados.

## Módulo entregue: gestão da base de conhecimento

A equipe (administradores e curadores) mantém os trechos da cartilha que a IA usa para responder.

**Fluxo completo:** entrar → ver a base (filtrar por tema e pesquisar no texto) → cadastrar um trecho → editar → excluir com confirmação. Tudo fica gravado no Supabase e continua disponível depois de fechar e abrir o sistema.

## O que foi entregue

| Item pedido | Entrega | Exemplos |
| --- | --- | --- |
| Módulo funcional | CRUD da base de conhecimento ligado ao banco, com os sinônimos da busca e os sites e vídeos do "Saber mais" | Telas **Base de conhecimento**, **Sinônimos da busca** e **Sites e vídeos** |
| Persistência | Dados no Supabase (PostgreSQL); o roteiro de evidências reinicia o sistema e confere que o trecho continua salvo | [`docs/ferramentas/capturar_evidencias.py`](../../ferramentas/capturar_evidencias.py) |
| Validações | No navegador (antes de enviar) e no servidor (regras iguais) | Subtítulo de 2 a 200 caracteres; texto de 10 a 5000; tema existente; e-mail válido; senha com no mínimo 8 caracteres |
| Mensagens de erro | Erros técnicos viram frases em português, junto do campo | "Preencha o campo subtítulo.", "Escolha um tema válido.", "Sem conexão com o servidor..." |
| Navegação | Rotas com menu por perfil; sem login vai para Entrar; perfil sem permissão vê um aviso; página 404 | [`frontend/src/App.jsx`](../../../frontend/src/App.jsx) |
| Commits organizados | Um commit por ajuste, com data, objetivo, o que foi feito e como agrega | [Histórico no GitHub](https://github.com/PedroHTLeal/oraculo_direitos_trabalhistas_8na/commits/main) |

## Ajustes desta Sprint

| Commit | O que mudou |
| --- | --- |
| [`5b2f043`](https://github.com/PedroHTLeal/oraculo_direitos_trabalhistas_8na/commit/5b2f043) | Tradução das mensagens de validação para o usuário |
| [`e5c21bf`](https://github.com/PedroHTLeal/oraculo_direitos_trabalhistas_8na/commit/e5c21bf) | Navegação do painel, validações nos formulários e confirmação antes de excluir |
| [`4165443`](https://github.com/PedroHTLeal/oraculo_direitos_trabalhistas_8na/commit/4165443) | Repetição automática quando a conexão com o banco cai; mensagem clara para erros inesperados |

## Evidências

Prints gerados em 02/11/2026 pelo roteiro automatizado [`capturar_evidencias.py`](../../ferramentas/capturar_evidencias.py), com o sistema rodando localmente e o banco real no Supabase. Todos os prints estão em [`docs/evidencias/`](../../evidencias/).

**Sinônimos da busca: palavras do dia a dia traduzidas para os termos da cartilha**

![Sinônimos da busca](../../evidencias/36-sinonimos.png)

**Sites e vídeos do "Saber mais", agrupados por assunto**

![Sites e vídeos do Saber mais](../../evidencias/37-sites-e-videos.png)

**Validação do cadastro de um link**

![Validação do cadastro de um link](../../evidencias/38-sites-e-videos-validacao.png)

**Consulta com filtro por tema e pesquisa no texto**

![Consulta com filtro por tema e pesquisa no texto](../../evidencias/12-base-filtro.png)

**Validação: campos obrigatórios do trecho**

![Validação: campos obrigatórios do trecho](../../evidencias/13-trecho-validacao.png)

**Cadastrar: trecho gravado e encontrado na pesquisa**

![Cadastrar: trecho gravado e encontrado na pesquisa](../../evidencias/14-trecho-cadastrado.png)

**Atualizar: edição do trecho**

![Atualizar: edição do trecho](../../evidencias/15-trecho-edicao.png)

**Mensagem de sucesso após salvar**

![Mensagem de sucesso após salvar](../../evidencias/16-trecho-atualizado.png)

**Persistência: o trecho continua salvo depois de fechar e abrir o sistema**

![Persistência: o trecho continua salvo depois de fechar e abrir o sistema](../../evidencias/20-persistencia-apos-reiniciar.png)

**Excluir: confirmação antes de apagar**

![Excluir: confirmação antes de apagar](../../evidencias/21-trecho-confirmar-exclusao.png)

**Excluir: trecho removido**

![Excluir: trecho removido](../../evidencias/22-trecho-excluido.png)

**Mensagens de erro junto de cada campo**

![Mensagens de erro junto de cada campo](../../evidencias/04-cadastro-validacao.png)

**Navegação no celular**

![Navegação no celular](../../evidencias/35-celular-painel.png)

