@echo off
rem Oraculo - liga a automacao do WhatsApp (n8n + WAHA) no Docker
setlocal
cd /d "%~dp0"

where docker >nul 2>nul || (
  echo [ERRO] Docker nao encontrado. Instale o Docker Desktop: https://www.docker.com/products/docker-desktop/
  echo Passo a passo: docs\configuracao.md, secao 3
  exit /b 1
)

if not exist .env (
  echo Criando automacao\.env com senhas aleatorias...
  powershell -NoProfile -Command "$t=[guid]::NewGuid().ToString('N'); $k=[guid]::NewGuid().ToString('N'); $s=[guid]::NewGuid().ToString('N').Substring(0,12); Set-Content -Encoding ascii .env @(\"ORACULO_TOKEN=$t\",\"WAHA_API_KEY=$k\",\"WAHA_SENHA_PAINEL=$s\")"
  echo Copie o valor de ORACULO_TOKEN para N8N_TOKEN no backend\.env
)

echo Ligando n8n e WAHA (na primeira vez o download demora alguns minutos)...
docker compose up -d || exit /b 1

echo.
echo n8n:  http://localhost:5678
echo WAHA: http://localhost:3000/dashboard  (usuario: admin, senha: WAHA_SENHA_PAINEL do automacao\.env)
start "" http://localhost:5678
start "" http://localhost:3000/dashboard
