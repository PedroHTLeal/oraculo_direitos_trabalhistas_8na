@echo off
rem Oraculo dos Direitos Trabalhistas - execucao local (Windows)
rem Prepara o backend e o frontend na primeira vez e abre o sistema em http://localhost:8000
setlocal
cd /d "%~dp0"

if not exist backend\.env (
  echo [ERRO] Arquivo backend\.env nao encontrado. Copie backend\.env.example para backend\.env e preencha as chaves.
  echo Passo a passo: docs\configuracao.md
  exit /b 1
)

if not exist backend\.venv (
  echo Criando o ambiente do Python...
  python -m venv backend\.venv || exit /b 1
)
echo Instalando as dependencias do backend...
backend\.venv\Scripts\python -m pip install -q -r backend\requirements.txt || exit /b 1

echo Compilando o frontend...
pushd frontend
call npm install --silent || exit /b 1
call npm run build || exit /b 1
popd

echo.
echo Oraculo rodando em http://localhost:8000  (Ctrl+C para encerrar)
start "" http://localhost:8000
backend\.venv\Scripts\python -m uvicorn app.main:app --app-dir backend --port 8000
