# Sprint 09 — Verificação completa e documentação

**Situação:** Em andamento · [← Voltar ao índice](../../README.md)

## O que a Sprint pediu

Testes funcionais, correção de bugs, testes de validação, testes de navegação e atualização da documentação técnica.

## Testes já existentes

| Tipo | Como é feito | Situação |
| --- | --- | --- |
| Testes automatizados do backend | 97 testes com `pytest` (rodar `pytest` na pasta `backend/`) | Todos passando |
| Testes funcionais | Login, cadastro, CRUD da base, usuários, temas, atualizações, relatórios, CSV e histórico | Cobertos pelos testes automatizados |
| Testes de validação | Campos obrigatórios, tamanhos, formatos (e-mail, telefone, link, datas) e regras de negócio | Cobertos pelos testes automatizados |
| Testes de navegação | Roteiro no navegador (Playwright + Edge) que percorre as telas e salva prints | [`capturar_evidencias.py`](../../ferramentas/capturar_evidencias.py) |

## Bugs

O registro dos bugs encontrados e corrigidos até agora está na [Sprint 05](../sprint-05/README.md#bugs-encontrados-e-corrigidos).

## Pendências

- Executar a bateria completa com o banco real e os serviços externos (Gemini e Twilio).
- Tabela de casos de teste com resultado esperado e obtido, com evidências.
- Revisão final da documentação técnica (diagramas, modelo de dados e instruções).
