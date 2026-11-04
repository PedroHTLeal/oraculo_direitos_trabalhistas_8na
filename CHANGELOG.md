# Histórico de versões

Registro de cada versão enviada ao GitHub: quando foi feita, qual o objetivo, o que mudou e como isso agrega ao projeto. As referências (RF, RNF, PB, UC) seguem o [relatório da Sprint 01](docs/sprints/sprint-01/relatorio.md).

---

## 0.12.0 — Integração contínua, avaliação da IA e requisitos atualizados

**Data:** 04/11/2026 · **Branch:** `main`

**Objetivo:** concluir os itens que faltavam no backlog (PB12 e PB19) e deixar o relatório com a situação real dos requisitos.

**O que foi feito:**
- [`.github/workflows/testes.yml`](.github/workflows/testes.yml): a cada envio ao GitHub, roda os 88 testes do backend e confere e compila o frontend (PB19, RNF12, RNF13).
- [`docs/ferramentas/avaliar_respostas.py`](docs/ferramentas/avaliar_respostas.py) e [`docs/avaliacao-ia.md`](docs/avaliacao-ia.md): avaliação das respostas da IA com 15 perguntas de referência (PB12, RNF08); 9 de 15 já avaliadas e aprovadas, e as demais ficam para quando a cota diária do plano gratuito renovar (o roteiro continua de onde parou).
- Relatório da Sprint 01: RF04 a RF14 e o backlog atualizados após os testes reais; integração contínua e publicação nas tecnologias.
- Sprint 09: caso CT27 (pergunta fora da cartilha, RF09).

**Como agrega:** todo envio passa a ser testado automaticamente, e a qualidade das respostas da IA fica medida e documentada.

---

## 0.11.0 — Relatório único de entrega (Sprints 01 a 09)

**Data:** 03/11/2026 · **Branch:** `main`

**Objetivo:** reunir todas as Sprints em um único PDF de entrega, no mesmo estilo do relatório da Sprint 01.

**O que foi feito:**
- [`docs/ferramentas/gerar_relatorio.py`](docs/ferramentas/gerar_relatorio.py) monta capa, índice com páginas, Sprint 01 (seções 1 a 14), Sprints 02 a 09, registro de decisões e histórico, com rodapé e numeração como no original.
- PDF gerado em [`docs/entrega/`](docs/entrega/) (63 páginas), com os prints refeitos e os diagramas da Sprint 02.

**Como agrega:** a entrega fica pronta e é regenerada com um comando sempre que a documentação muda.

---

## 0.10.2 — Registro de decisões e mudanças de escopo

**Data:** 03/11/2026 · **Branch:** `main`

**Objetivo:** mostrar o que foi pensado e testado ao longo do projeto e por que algumas ideias não foram usadas.

**O que foi feito:**
- Novo documento [`docs/decisoes.md`](docs/decisoes.md): troca do Claude pelo Gemini; WhatsApp pela Twilio, pela API da Meta e pelo n8n (WAHA e Evolution API) até a escolha do e-mail; pesquisa automática de links até os links escolhidos pela equipe; GitHub Pages e Render até a Vercel.
- Ligado à Sprint 08 (registro das mudanças de escopo), à Sprint 06 e ao índice da documentação.

**Como agrega:** deixa claro o raciocínio da equipe em cada escolha, com o commit de cada momento.

---

## 0.10.1 — Ajustes de usabilidade na consulta

**Data:** 03/11/2026 · **Branch:** `main`

**Objetivo:** deixar a consulta mais direta, a partir da revisão da equipe com o sistema publicado.

**O que foi feito:**
- O botão "Entrar" saiu do topo da tela de consulta; a equipe entra pelo endereço `/entrar`.
- As fontes mostram cada seção da cartilha uma vez, só com o link "Ver na cartilha", sem repetir o texto da resposta.
- O botão "Receber por e-mail" só fica disponível com nome, e-mail e a autorização da LGPD.

**Como agrega:** menos distrações e menos repetição para quem consulta, e consentimento mais claro (RNF03). Registrado na [Sprint 08](docs/sprints/sprint-08/README.md).

---

## 0.10.0 — Pronto para publicar na Vercel

**Data:** 03/11/2026 · **Branch:** `main`

**Objetivo:** permitir apresentar o Oráculo por um endereço público, sem custo.

**O que foi feito:**
- `vercel.json`, `api/index.py` e `requirements.txt` na raiz: a Vercel monta o site React e publica o backend FastAPI como função Python, na região de São Paulo.
- Na Vercel, os envios de e-mail ("Saber mais" e novidades) acontecem dentro do próprio pedido, porque a função para logo depois de responder (`backend/app/segundo_plano.py`).
- Guia passo a passo em [`docs/publicacao.md`](docs/publicacao.md), com a comparação com o GitHub Pages.

**Como agrega:** atende à entrega (DevOps Tools) com o sistema acessível de qualquer lugar e atualizado automaticamente a cada envio ao GitHub.

---

## 0.9.2 — E-mail com a identidade visual do Oráculo

**Data:** 03/11/2026 · **Branch:** `main`

**Objetivo:** deixar o e-mail do "Saber mais" e das novidades com a mesma cara do site.

**O que foi feito:**
- Novo modelo de e-mail: cabeçalho azul-escuro com o logo do Oráculo, a balança dourada e a pergunta em destaque, resposta da cartilha, sites e vídeos em cartões e rodapé com a frase do site.
- Logo e balança em PNG, anexados ao próprio e-mail (o Gmail não exibe SVG), gerados por `backend/scripts/gerar_imagens_email.py`.
- O e-mail de novidades dos temas usa a mesma moldura, com o botão "Saiba mais".

**Como agrega:** reforça a identidade do Oráculo fora do site e deixa os links mais fáceis de encontrar e tocar no celular.

---

## 0.9.1 — Sites e vídeos escolhidos pela equipe

**Data:** 02/11/2026 · **Branch:** `main`

**Objetivo:** enviar no "Saber mais" links confiáveis, escolhidos pela equipe, sem depender de pesquisa por API (o plano gratuito do Gemini não libera a pesquisa no Google).

**O que foi feito:**
- Nova tabela `materiais_complementares` ([`supabase/007_materiais_complementares.sql`](supabase/007_materiais_complementares.sql)) com os primeiros assuntos: férias e 13º salário.
- O assunto é escolhido pelas palavras-chave da pergunta (`backend/app/materiais.py`); sem assunto cadastrado, vão a página da cartilha do TRT4, o texto oficial da lei e uma busca pronta no YouTube.
- A pesquisa na web pelo Gemini foi retirada; a IA continua só escrevendo a resposta a partir da cartilha.
- Quando o modelo principal do Gemini está sobrecarregado, a resposta usa um modelo reserva.

**Como agrega:** os endereços enviados são sempre reais e conferidos, o envio fica mais rápido e não esbarra em limites de API.

---

## 0.9.0 — Conteúdo complementar e novidades por e-mail

**Data:** 02/11/2026 · **Branch:** `main`

**Objetivo:** tornar o "Saber mais" simples e rápido: a pessoa informa só o nome e o e-mail e recebe a resposta, 2 sites e 2 vídeos do YouTube sobre o assunto (decisão da equipe).

**O que foi feito:**
- Novo envio de e-mails pelo Gmail (`backend/app/envio_email.py`), com versão em texto e em HTML nas cores do Oráculo.
- Janela "Saber mais" com nome, e-mail e autorização (LGPD), sem exigir conta; quem já entrou tem os campos preenchidos.
- Limite de 5 pedidos por e-mail a cada hora, para o formulário não ser usado para spam.
- Contas com e-mail e senha para todos os perfis; as novidades dos temas acompanhados também chegam por e-mail.
- Banco ajustado pelo [`supabase/006_contato_por_email.sql`](supabase/006_contato_por_email.sql).
- Guia de configuração com o passo a passo da senha de app do Gmail; documentação das Sprints atualizada; 91 testes no backend.

**Como agrega:** atende RF10, RF11 e UC05 do jeito mais simples para quem usa: nada para instalar, sem custo e sem precisar criar conta para receber o conteúdo.

---

## 0.6.0 — Sprints 03 a 09: login, módulos, relatórios e testes

**Data:** 31/10/2026 a 02/11/2026 · **Branch:** `main` (os ajustes de cada Sprint estão em [`docs/sprints/`](docs/sprints/))

**Objetivo:** cumprir as entregas práticas das Sprints 03 a 09.

**O que foi feito:**
- Login, cadastro e perfis (administrador, curador, usuário); cadastro público com nome e senha.
- Módulo 1: CRUD da base de conhecimento. Módulo 2: temas acompanhados e atualizações enviadas aos inscritos. Módulo 3: consulta com IA integrada aos outros dois.
- Dashboard, relatórios com filtros, exportação em CSV e histórico de operações.
- Deploy local com `iniciar.bat`; branches consolidados em um único `main`.
- 97 testes automatizados, 35 passos testados no banco real e 6 bugs corrigidos.
- Convite "Quer saber mais sobre o assunto? Sim", com explicação antes do cadastro.

**Como agrega:** o sistema passa a ter os três módulos funcionando e integrados, com evidências reais de cada Sprint.

---

## 0.5.0 — IA gratuita com Google Gemini

**Data:** 31/10/2026 · **Branch:** `base-conhecimento` · **Integração:** junto com as versões 0.4.x

**Objetivo:** manter o projeto sem nenhum custo, trocando a IA paga (Claude, da Anthropic) pelo plano gratuito do Google Gemini.

**O que foi feito:**
- As respostas passaram a ser geradas pelo Gemini (`gemini-flash-latest`), com as mesmas regras: usar só os trechos da cartilha, linguagem simples e indicação das fontes.
- Os 2 sites e os 2 vídeos enviados passaram a ser pesquisados pelo próprio Gemini.
- Se a pesquisa não trouxer vídeos, a mensagem indica uma busca pronta no YouTube sobre o tema.
- Novos testes da integração com o Gemini (42 no total).
- Guia de configuração, modelo do `.env`, README e relatório atualizados.

**Como agrega ao projeto:**
- Atende ao RNF09 (custo operacional): IA e banco de dados agora usam apenas planos gratuitos.
- Uma única chave do Google cobre a geração das respostas e a pesquisa de materiais, simplificando a configuração.
- Os links enviados continuam vindo só de resultados reais da pesquisa, evitando endereços inventados.

**Pendente:** testar com a chave do Gemini.

---

## 0.4.1 — Busca validada no Supabase real

**Data:** 31/10/2026 · **Branch:** `base-conhecimento` · **Integração:** junto com a versão 0.4.0

**Objetivo:** carregar a cartilha no Supabase do projeto e garantir que a busca encontre os trechos certos para perguntas escritas do jeito que as pessoas falam.

**O que foi feito:**
- Os 217 trechos da cartilha foram carregados no Supabase.
- Correção de um erro na função de busca: as palavras da pergunta eram processadas duas vezes e termos como "estágio" não eram encontrados (`supabase/002_corrige_busca_e_sinonimos.sql`).
- Nova tabela de sinônimos com 41 expressões do dia a dia (ex.: "demitido" → "dispensa", "patrão" → "empregador", "grávida" → "gestante"), editável pelo administrador.
- Limite de 3 trechos por tema na busca, para a IA receber mais de um assunto quando a pergunta envolve vários.
- Novo teste automatizado (36 no total) e guia de configuração atualizado com o segundo arquivo SQL.

**Como agrega ao projeto:**
- Valida com dados reais a parte de recuperação do RAG (PB06, RF04): perguntas como "Empregada doméstica tem FGTS?" e "Fui humilhado pelo meu chefe" agora encontram os temas Fundo de Garantia e Danos Morais.
- Aproxima a linguagem do público-alvo (pessoas sem familiaridade com termos jurídicos) da linguagem da cartilha.
- Mostra na prática a importância de testar com o ambiente real: o erro não aparecia nos testes com dados simulados.

**Pendente:** testar a geração das respostas e o envio do conteúdo complementar com as chaves reais.

---

## 0.4.0 — Base de conhecimento, respostas com IA e conteúdo complementar

**Data:** 31/10/2026 · **Branch:** `base-conhecimento` · **Integração:** Pull Request para `main`, após `tela-perguntas` e `novo-visual`

**Objetivo:** fazer o Oráculo responder de verdade, com base na cartilha do TRT4 guardada no Supabase, e permitir que o usuário receba conteúdo complementar (2 sites e 2 vídeos).

**O que foi feito:**
- Extração automática das 25 páginas da Cartilha de Direitos e Obrigações no Trabalho do TRT4, divididas em 217 trechos com tema, seção e link da fonte.
- Estrutura do banco no Supabase: tabelas de trechos, perguntas e pedidos de conteúdo complementar, busca textual em português que ignora acentos e acesso público bloqueado.
- Respostas geradas pela IA (Claude) usando somente os trechos encontrados, em linguagem simples, com as fontes conferidas pelo sistema.
- A resposta aparece no painel azul, no lugar da órbita de temas; no celular, abaixo do campo de pergunta.
- Botão "Saiba mais": pede o contato e o consentimento (LGPD); a IA pesquisa 2 sites e 2 vídeos do YouTube, e o Oráculo envia tudo ao usuário.
- Registro de erros no servidor e situação de cada pedido no banco.
- Guia de configuração das contas (`docs/configuracao.md`) e modelo do arquivo de chaves (`backend/.env.example`).
- 35 testes automatizados no backend (antes eram 7).

**Como agrega ao projeto:**
- Implementa o núcleo do sistema: RF04 a RF11, os casos de uso UC01 a UC05 e os itens PB02, PB05, PB06, PB07 e PB08 do backlog.
- Adianta a implementação do RAG e da IA, prevista para a Sprint 04.
- A IA só usa a cartilha e o sistema confere as fontes citadas, o que reduz respostas inventadas (RNF08).
- Os links e vídeos enviados são só os encontrados de fato na pesquisa, evitando endereços inventados.
- O consentimento obrigatório, a validação do contato e o bloqueio de acesso público ao banco atendem ao RNF03 (LGPD).

**Pendente:** o teste com os serviços reais depende da criação das contas no Supabase e na IA.

---

## 0.3.1 — Nova paleta de cores

**Data:** 31/10/2026 · **Branch:** `novo-visual` · **Integração:** junto com a versão 0.3.0

**Objetivo:** dar ao Oráculo uma paleta própria, trocando o verde neon e o azul-marinho herdados do FlowFocus por dourado e azul-escuro.

**O que foi feito:**
- Cor principal alterada de azul-marinho `#0C236F` para azul-escuro `#030C2C` (botões, tema selecionado e painel lateral).
- Cor de destaque alterada de verde neon `#07F98B` para dourado `#E8B20F` (núcleo da órbita, ponto do logotipo e detalhes do tema selecionado).
- O botão "Perguntar" fica dourado ao passar o mouse.
- O indicador de foco do teclado passou a ser azul-escuro, porque o dourado tem pouco contraste sobre o fundo branco.
- Relatório: seção 14 atualizada com a nova paleta.

**Como agrega ao projeto:**
- Diferencia a identidade do Oráculo da referência visual usada. O dourado remete a valor e confiança, e o azul-escuro a seriedade, combinação comum em temas jurídicos.
- Mantém a acessibilidade (RNF02): o foco do teclado continua bem visível e os textos seguem com bom contraste.

---

## 0.3.0 — Novo visual

**Data:** 31/10/2026 · **Branch:** `novo-visual` · **Integração:** Pull Request para `main`, após a integração de `tela-perguntas`

**Objetivo:** deixar a plataforma mais bonita e com identidade própria, seguindo o estilo visual do FlowFocus, para transmitir confiança e tornar o uso mais agradável.

**O que foi feito:**
- Identidade visual: logotipo do Oráculo, fonte Plus Jakarta Sans e paleta azul-marinho (`#0C236F`) com verde de destaque (`#07F98B`).
- Layout dividido em computadores: conteúdo à esquerda e painel azul à direita, com os temas girando em órbita ao redor de uma balança da justiça e uma frase sobre o propósito do sistema.
- Temas sugeridos exibidos como cartões, com destaque em azul no tema selecionado.
- Campo de pergunta e cartão de resposta redesenhados, com bordas suaves e cantos arredondados.
- No celular, o painel azul é ocultado para priorizar o conteúdo.
- Acessibilidade: indicador de foco visível para navegação por teclado, áreas de toque de no mínimo 44px e animação desativada para quem prefere reduzir movimento.
- Relatório: nova seção 14 (Identidade Visual).

**Como agrega ao projeto:**
- Reforça RNF01 e RNF02 (experiência simples e acessível em celular e computador) e avança PB04 (frontend).
- Uma aparência profissional transmite confiança, o que é importante para um sistema que orienta sobre direitos.
- Define a identidade visual do projeto, item que constava no índice do relatório original e agora tem conteúdo próprio.

---

## 0.2.0 — Tela de perguntas

**Data:** 31/10/2026 · **Branch:** `tela-perguntas` · **Integração:** Pull Request para `main`

**Objetivo:** entregar a primeira tela funcional do sistema, permitindo que o usuário faça perguntas (UC01), e manter o relatório da Sprint 01 atualizado junto com o código.

**O que foi feito:**
- Backend: rota de temas e perguntas sugeridos e rota de envio de perguntas, que por enquanto devolve uma resposta provisória já no formato final (resposta, fontes e indicação se encontrou informação).
- Backend: validação das perguntas (vazias, com menos de 3 ou mais de 500 caracteres são rejeitadas) e 6 novos testes automatizados, totalizando 7.
- Frontend: campo de pergunta livre, temas sugeridos, cartão de resposta preparado para exibir fontes e link para o conteúdo original, aviso quando não há informação suficiente e layout adaptado para celular.
- Documentação: versão editável e atualizada do relatório da Sprint 01 (`docs/sprints/sprint-01/relatorio.md`), com correção da seção 4, situação dos requisitos e do backlog, tecnologias definidas e fluxo de branches com Pull Requests.
- Este arquivo de histórico de versões.

**Como agrega ao projeto:**
- Atende RF01, RF02 e RF03 e prepara RF07, RF08 e RF09, além de RNF01 e RNF02 (uso em celular e computador).
- Como o formato da resposta já é o definitivo, quando o RAG (PB06) for implementado basta trocar a lógica da API, sem alterar a tela.
- Os testes aumentam a segurança para evoluir o código (PB11, PB18, RNF12).
- O relatório e o histórico de versões mantêm a documentação alinhada ao código (PB15) e servem de evidência do processo para as três disciplinas.

---

## 0.1.0 — Estrutura inicial do projeto

**Data:** 31/10/2026 · **Branch:** `main`

**Objetivo:** criar a base do repositório e do ambiente de desenvolvimento, com as tecnologias definidas para o projeto.

**O que foi feito:**
- README com a proposta, o problema, os objetivos, o público-alvo e as instruções para executar o projeto.
- `.gitignore` para evitar o envio de segredos (`.env`), dependências e arquivos temporários.
- Backend em Python 3.12 com FastAPI, com uma rota que verifica se a API está no ar e o primeiro teste com pytest.
- Frontend em React com Vite, com ESLint configurado e comunicação com o backend durante o desenvolvimento.
- Pasta `docs/` para a documentação das Sprints.

**Como agrega ao projeto:**
- Define as tecnologias que estavam "a definir" no relatório: Python (com acesso às principais bibliotecas de IA e RAG) e React (interface responsiva).
- Atende RNF10 e RNF11 (controle de versão e organização do repositório) e inicia PB03, PB04, PB16 e PB17.
- Adianta a "Estruturação do ambiente de desenvolvimento", prevista para a Sprint 02.
