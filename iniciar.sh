#!/usr/bin/env sh
# Oráculo dos Direitos Trabalhistas - execução local (Linux e macOS)
# Prepara o backend e o frontend na primeira vez e abre o sistema em http://localhost:8000
set -e
cd "$(dirname "$0")"

if [ ! -f backend/.env ]; then
  echo "[ERRO] Arquivo backend/.env não encontrado. Copie backend/.env.example para backend/.env e preencha as chaves."
  echo "Passo a passo: docs/configuracao.md"
  exit 1
fi

[ -d backend/.venv ] || python3 -m venv backend/.venv
echo "Instalando as dependências do backend..."
backend/.venv/bin/python -m pip install -q -r backend/requirements.txt

echo "Compilando o frontend..."
(cd frontend && npm install --silent && npm run build)

echo
echo "Oráculo rodando em http://localhost:8000  (Ctrl+C para encerrar)"
backend/.venv/bin/python -m uvicorn app.main:app --app-dir backend --port 8000
