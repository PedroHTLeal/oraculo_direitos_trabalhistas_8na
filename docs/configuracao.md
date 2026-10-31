# Configuração dos serviços externos

O Oráculo usa três serviços, todos com plano gratuito. Cada um precisa de uma conta e de chaves, que ficam no arquivo `backend/.env` (esse arquivo **nunca** vai para o GitHub).

Antes de começar, copie o modelo:

```bash
cp backend/.env.example backend/.env
```

## 1. Supabase (banco de dados)

Guarda a cartilha do TRT4, as perguntas feitas e os pedidos de WhatsApp.

1. Crie uma conta em https://supabase.com e clique em **New project** (plano gratuito).
2. Escolha um nome (ex.: `oraculo`), uma senha para o banco e a região **South America (São Paulo)**.
3. Quando o projeto estiver pronto, abra **SQL Editor** e execute, nesta ordem, cada arquivo da pasta [`supabase/`](../supabase/) (cole todo o conteúdo e clique em **Run**):
   1. [`001_estrutura_inicial.sql`](../supabase/001_estrutura_inicial.sql)
   2. [`002_corrige_busca_e_sinonimos.sql`](../supabase/002_corrige_busca_e_sinonimos.sql)
4. Em **Project Settings > API**, copie para o `backend/.env`:
   - **Project URL** → `SUPABASE_URL`
   - **service_role** (em *Project API keys*) → `SUPABASE_SERVICE_ROLE_KEY`

   > A chave `service_role` dá acesso total ao banco: use só no backend e nunca a coloque no frontend.

5. Carregue a cartilha no banco (na pasta `backend/`, com o ambiente virtual ativo):

   ```bash
   python scripts/carregar_cartilha.py
   ```

Para atualizar a cartilha no futuro, rode `python scripts/extrair_cartilha.py` e depois `python scripts/carregar_cartilha.py`.

## 2. Google Gemini (inteligência artificial, gratuito)

Gera as respostas a partir dos trechos da cartilha e pesquisa no Google os sites e vídeos enviados pelo WhatsApp. O plano gratuito não pede cartão de crédito.

1. Acesse https://aistudio.google.com e entre com uma conta Google.
2. Aceite os termos de uso, se aparecerem.
3. Clique em **Get API key** (ou **Criar chave de API**) e depois em **Create API key**. Se pedir um projeto, deixe o Google criar um novo.
4. Copie a chave (começa com `AIza`) para `GEMINI_API_KEY`.

> O plano gratuito tem limites diários de uso, suficientes para testes e para a apresentação. Nesse plano, o Google pode usar o conteúdo das requisições para melhorar seus produtos; por isso, o Oráculo envia à IA apenas a pergunta e os trechos da cartilha, nunca o telefone do usuário.

## 3. Twilio (WhatsApp)

Envia a mensagem com a resposta, os sites e os vídeos. No ambiente de teste (Sandbox), é gratuito.

1. Crie uma conta em https://www.twilio.com/try-twilio.
2. No painel inicial (**Account Info**), copie:
   - **Account SID** → `TWILIO_ACCOUNT_SID`
   - **Auth Token** → `TWILIO_AUTH_TOKEN`
3. Abra **Messaging > Try it out > Send a WhatsApp message**. A página mostra:
   - o número do Sandbox (ex.: `+1 415 523 8886`) → `TWILIO_WHATSAPP_NUMERO` (sem espaços: `+14155238886`)
   - o código de entrada (ex.: `join palavra-palavra`) → `TWILIO_SANDBOX_CODIGO`
4. **Pelo seu celular**, envie esse código para o número do Sandbox no WhatsApp. Só depois disso o número passa a receber as mensagens do Oráculo.

> No Sandbox, **cada celular que for receber mensagens** precisa enviar o código antes (a tela do Oráculo mostra essa instrução). O WhatsApp só permite esse tipo de mensagem até 24 horas depois da última mensagem enviada pelo usuário ao número; se passar disso, envie o código de novo. Em produção, o envio usa um número de WhatsApp aprovado e modelos de mensagem, e esse passo deixa de existir.

## 4. Conferir

Reinicie o backend e faça uma pergunta na tela. Se aparecer "O serviço ainda não foi configurado", alguma variável do `backend/.env` está vazia: o nome dela aparece no terminal do backend.
