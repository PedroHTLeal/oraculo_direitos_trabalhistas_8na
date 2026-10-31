# Histórico de versões

Registro de cada versão enviada ao GitHub: quando foi feita, qual o objetivo, o que mudou e como isso agrega ao projeto. As referências (RF, RNF, PB, UC) seguem o [relatório da Sprint 01](docs/sprint-01/relatorio.md).

---

## 0.5.0 — IA gratuita com Google Gemini

**Data:** 31/10/2026 · **Branch:** `base-conhecimento` · **Integração:** junto com as versões 0.4.x

**Objetivo:** manter o projeto sem nenhum custo, trocando a IA paga (Claude, da Anthropic) pelo plano gratuito do Google Gemini.

**O que foi feito:**
- As respostas passaram a ser geradas pelo Gemini (`gemini-flash-latest`), com as mesmas regras: usar só os trechos da cartilha, linguagem simples e indicação das fontes.
- Os 2 sites e os 2 vídeos enviados pelo WhatsApp passaram a ser pesquisados no Google pelo próprio Gemini. O sistema segue cada link da pesquisa até o endereço final e busca o título real da página ou do vídeo.
- Se a pesquisa não trouxer vídeos, a mensagem indica uma busca pronta no YouTube sobre o tema.
- Novos testes da integração com o Gemini (42 no total).
- Guia de configuração, modelo do `.env`, README e relatório atualizados.

**Como agrega ao projeto:**
- Atende ao RNF09 (custo operacional): IA, banco de dados e WhatsApp agora usam apenas planos gratuitos.
- Uma única chave do Google cobre a geração das respostas e a pesquisa de materiais, simplificando a configuração.
- Os links enviados continuam vindo só de resultados reais da pesquisa, evitando endereços inventados.

**Pendente:** testar com as chaves do Gemini e da Twilio.

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

**Pendente:** testar a geração das respostas e o envio pelo WhatsApp, que dependem das chaves da Anthropic e da Twilio.

---

## 0.4.0 — Base de conhecimento, respostas com IA e WhatsApp

**Data:** 31/10/2026 · **Branch:** `base-conhecimento` · **Integração:** Pull Request para `main`, após `tela-perguntas` e `novo-visual`

**Objetivo:** fazer o Oráculo responder de verdade, com base na cartilha do TRT4 guardada no Supabase, e permitir que o usuário receba conteúdo complementar (2 sites e 2 vídeos) no WhatsApp.

**O que foi feito:**
- Extração automática das 25 páginas da Cartilha de Direitos e Obrigações no Trabalho do TRT4, divididas em 217 trechos com tema, seção e link da fonte.
- Estrutura do banco no Supabase: tabelas de trechos, perguntas e pedidos de WhatsApp, busca textual em português que ignora acentos e acesso público bloqueado.
- Respostas geradas pela IA (Claude) usando somente os trechos encontrados, em linguagem simples, com as fontes conferidas pelo sistema.
- A resposta aparece no painel azul, no lugar da órbita de temas; no celular, abaixo do campo de pergunta.
- Botão "Saiba mais pelo WhatsApp": pede o telefone e o consentimento (LGPD); a IA pesquisa 2 sites e 2 vídeos do YouTube, e a Twilio envia tudo para o WhatsApp do usuário.
- Registro de erros no servidor e situação de cada pedido no banco.
- Guia de configuração das contas (`docs/configuracao.md`) e modelo do arquivo de chaves (`backend/.env.example`).
- 35 testes automatizados no backend (antes eram 7).

**Como agrega ao projeto:**
- Implementa o núcleo do sistema: RF04 a RF11, os casos de uso UC01 a UC05 e os itens PB02, PB05, PB06, PB07 e PB08 do backlog.
- Adianta a implementação do RAG e da IA, prevista para a Sprint 04.
- A IA só usa a cartilha e o sistema confere as fontes citadas, o que reduz respostas inventadas (RNF08).
- Os links e vídeos enviados são só os encontrados de fato na pesquisa, evitando endereços inventados.
- O consentimento obrigatório, a validação do telefone e o bloqueio de acesso público ao banco atendem ao RNF03 (LGPD).

**Pendente:** o teste com os serviços reais depende da criação das contas no Supabase, na Anthropic e na Twilio.

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
- Documentação: versão editável e atualizada do relatório da Sprint 01 (`docs/sprint-01/relatorio.md`), com correção da seção 4, situação dos requisitos e do backlog, tecnologias definidas e fluxo de branches com Pull Requests.
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
