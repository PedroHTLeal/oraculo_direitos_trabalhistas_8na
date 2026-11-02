# Sprint 06 — Módulo 3, integração e melhorias de interface

**Situação:** Em andamento: módulo 3 e integração prontos no código; aguarda as observações da Pré-Banca e a chave do Gemini · [← Voltar ao índice](../../README.md)

## O que a Sprint pediu

Correções apontadas na Pré-Banca, terceiro módulo implementado, integração entre os módulos, melhorias na interface e ajustes de navegação.

## Módulo entregue: consulta inteligente (componente de IA)

**Fluxo:** a pessoa faz a pergunta → o sistema busca os trechos mais relevantes da cartilha no Supabase → a IA (Google Gemini) escreve a resposta usando só esses trechos → a resposta aparece com as fontes → "Saiba mais" envia resposta, 2 sites e 2 vídeos pelo WhatsApp.

## Integração entre os módulos

| De | Para | Como |
| --- | --- | --- |
| Módulo 1 (base de conhecimento) | Módulo 3 (consulta) | Todo trecho cadastrado ou editado pela equipe passa a ser usado pela IA nas respostas |
| Módulo 3 (consulta) | Módulo 1 (base) | Perguntas sem resposta aparecem no Dashboard e no relatório com o botão **Incluir na base** |
| Módulo 2 (conta com WhatsApp) | Módulo 3 (consulta) | O "Saiba mais" envia para o telefone da conta; sem conta, a janela oferece criar a conta sem perder a resposta |
| Todos | Histórico e Dashboard | Operações registradas no histórico e somadas nos indicadores ([Sprint 07](../sprint-07/README.md)) |

## O que foi entregue

| Item pedido | Situação |
| --- | --- |
| Correções da Pré-Banca | **Pendente:** aguardando as observações recebidas pela equipe |
| Terceiro módulo | Implementado; a geração de respostas aguarda a chave gratuita do Gemini no `backend/.env` |
| Integração entre módulos | Concluída (tabela acima) |
| Melhorias na interface | Formulários de conta reaproveitados; abas na janela "Saiba mais"; menu por perfil; páginas iniciais por perfil (equipe → Dashboard, usuário → Meus temas) |
| Ajustes de navegação | Depois de sair, a pessoa vai para "Entrar"; o topo da página leva cada perfil à sua área; "Meus temas" só aparece para quem recebe pelo WhatsApp |

## Ajustes desta Sprint

| Commit | O que mudou |
| --- | --- |
| [`10f67db`](https://github.com/PedroHTLeal/oraculo_direitos_trabalhistas_8na/commit/10f67db) | Busca na base, resposta com IA e "Saiba mais" pelo WhatsApp |
| [`231dc75`](https://github.com/PedroHTLeal/oraculo_direitos_trabalhistas_8na/commit/231dc75) | IA trocada pelo Google Gemini gratuito (projeto sem custo) |
| [`7f76733`](https://github.com/PedroHTLeal/oraculo_direitos_trabalhistas_8na/commit/7f76733) | "Saiba mais" integrado à conta com WhatsApp |
| [`04f09ab`](https://github.com/PedroHTLeal/oraculo_direitos_trabalhistas_8na/commit/04f09ab) | Integração "Incluir na base" a partir das perguntas sem resposta; menu por perfil |

## Mudanças em relação ao planejado

- **IA:** a primeira versão usava o Claude (Anthropic), que é pago; foi trocado pelo **Google Gemini** no plano gratuito, para atender ao RNF09 (custo operacional).
- **Links e vídeos:** são pesquisados pelo próprio Gemini no Google; o sistema só envia endereços que vieram da pesquisa real.
