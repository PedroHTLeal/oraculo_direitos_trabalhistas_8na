# Automação do WhatsApp (n8n + Evolution API)

O Oráculo envia o WhatsApp por um fluxo do **n8n** (backlog **PB09 – Automação com n8n**), que usa a **Evolution API** para conectar um WhatsApp por QR code. Tudo roda no seu computador, de graça, pelo Docker.

```
Oráculo (backend)
   │  POST /webhook/oraculo-whatsapp   { telefone, mensagem }  + cabeçalho X-Oraculo-Token
   ▼
n8n ─ Validar pedido ─ Conferir número no WhatsApp ─ Número tem WhatsApp? ─ Enviar mensagem
   │                                                                          │
   ▼                                                                          ▼
Evolution API (instância "oraculo", conectada por QR code) ──────▶ WhatsApp da pessoa
```

| Arquivo | Para que serve |
| --- | --- |
| [`docker-compose.yml`](docker-compose.yml) | Sobe o n8n (porta 5678), a Evolution API (porta 8080) e o banco PostgreSQL dela |
| [`fluxo-oraculo-whatsapp.json`](fluxo-oraculo-whatsapp.json) | Fluxo para importar no n8n |
| [`iniciar-automacao.bat`](iniciar-automacao.bat) | Cria o `.env` com senhas aleatórias (na primeira vez) e liga tudo |
| [`.env.example`](.env.example) | Modelo das senhas; o `.env` real nunca vai para o GitHub |

## O que o fluxo faz

1. **Pedido do Oráculo:** recebe o telefone e a mensagem.
2. **Validar pedido:** confere o token combinado com o Oráculo (`ORACULO_TOKEN` = `N8N_TOKEN` do `backend/.env`).
3. **Conferir número no WhatsApp:** pergunta à Evolution API como o número está registrado no WhatsApp; isso resolve o 9 extra dos celulares brasileiros.
4. **Número tem WhatsApp?:** para com uma mensagem clara se o número não tiver WhatsApp.
5. **Enviar mensagem:** envia o texto pela instância `oraculo` da Evolution API.

Cada execução fica registrada no n8n (menu **Executions**), útil para demonstrar e para encontrar erros.

## Passo a passo

Veja o [guia de configuração, seção 3](../docs/configuracao.md#3-whatsapp-com-n8n-e-evolution-api-gratuito-no-seu-computador).

> **Risco conhecido:** a Evolution API usa o WhatsApp Web, que não é um serviço oficial e vai contra os termos de uso do WhatsApp. Use um número secundário, só para o Oráculo.
