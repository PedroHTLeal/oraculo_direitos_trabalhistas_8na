# Sprint 04 — Módulo 1: gestão da base de conhecimento

**Situação:** Concluída no código; evidências com o banco real em produção · [← Voltar ao índice](../../README.md)

## O que a Sprint pediu

Primeiro módulo totalmente funcional, com persistência de dados, validações, mensagens de erro claras, navegação entre telas e commits organizados.

## Módulo entregue: gestão da base de conhecimento

A equipe (administradores e curadores) mantém os trechos da cartilha que a IA usa para responder.

**Fluxo completo:** entrar → ver a base (filtrar por tema e pesquisar no texto) → cadastrar um trecho → editar → excluir com confirmação. Tudo fica gravado no Supabase e continua disponível depois de fechar e abrir o sistema.

## O que foi entregue

| Item pedido | Entrega | Exemplos |
| --- | --- | --- |
| Módulo funcional | CRUD da base de conhecimento ligado ao banco | Tela **Base de conhecimento** |
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

Os prints ficam em `docs/evidencias/` e são gerados pelo roteiro automatizado [`capturar_evidencias.py`](../../ferramentas/capturar_evidencias.py), que percorre os fluxos no navegador.
