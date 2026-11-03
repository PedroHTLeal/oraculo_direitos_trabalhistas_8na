# Ferramentas

| Arquivo | Para que serve |
| --- | --- |
| [`capturar_evidencias.py`](capturar_evidencias.py) | Percorre as telas do sistema no navegador (Playwright + Microsoft Edge) com as contas de demonstração e salva um print de cada passo em `docs/evidencias/`. Serve de teste de navegação e de evidência para os relatórios. |
| [`gerar_relatorio.py`](gerar_relatorio.py) | Gera o relatório único de entrega em PDF (Sprints 01 a 09), no estilo do relatório da Sprint 01, juntando o relatório, as páginas das Sprints, os diagramas e o registro de decisões. Saída em `docs/entrega/`. |

## Como usar

1. Crie as contas de demonstração (uma por perfil; as senhas ficam só no `backend/.env`):

   ```bash
   backend\.venv\Scripts\python backend\scripts\criar_contas_demonstracao.py
   ```

2. Com o sistema rodando em http://localhost:8000 (`iniciar.bat`), execute:

   ```bash
   backend\.venv\Scripts\python docs\ferramentas\capturar_evidencias.py criar
   ```

3. Feche e abra o sistema de novo (para provar a persistência dos dados) e execute:

   ```bash
   backend\.venv\Scripts\python docs\ferramentas\capturar_evidencias.py conferir
   ```

## Gerar o PDF de entrega

Depois de atualizar a documentação de alguma Sprint, rode:

```bash
backend\.venv\Scripts\python docs\ferramentas\gerar_relatorio.py
```

O PDF fica em `docs/entrega/`. A capa usa o brasão em `logo-cabecalho.png` (retirado do relatório original) e os diagramas são desenhados a partir dos blocos `mermaid` dos documentos (precisa de internet para carregar as fontes e o Mermaid).
