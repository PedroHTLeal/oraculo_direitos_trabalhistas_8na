# Ferramentas

| Arquivo | Para que serve |
| --- | --- |
| [`capturar_evidencias.py`](capturar_evidencias.py) | Percorre as telas do sistema no navegador (Playwright + Microsoft Edge) com as contas de demonstração e salva um print de cada passo em `docs/evidencias/`. Serve de teste de navegação e de evidência para os relatórios. |

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
