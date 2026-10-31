# Histórico de versões

Registro de cada versão enviada ao GitHub: quando foi feita, qual o objetivo, o que mudou e como isso agrega ao projeto. As referências (RF, RNF, PB, UC) seguem o [relatório da Sprint 01](docs/sprint-01/relatorio.md).

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
