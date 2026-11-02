# Configuração dos serviços externos

O Oráculo usa três serviços (banco, IA e WhatsApp), todos com plano gratuito. Cada um precisa de uma conta e de chaves, que ficam no arquivo `backend/.env` (esse arquivo **nunca** vai para o GitHub).

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
   3. [`003_modelo_relacional.sql`](../supabase/003_modelo_relacional.sql)
   4. [`004_conta_com_whatsapp.sql`](../supabase/004_conta_com_whatsapp.sql)
   5. [`005_historico_de_operacoes.sql`](../supabase/005_historico_de_operacoes.sql)
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

## 3. WhatsApp

O Oráculo envia o WhatsApp por um destes serviços, escolhido na linha `PROVEDOR_WHATSAPP` do `backend/.env`:

| Valor | Serviço | Quando usar |
| --- | --- | --- |
| `meta` | **WhatsApp Cloud API**, a API oficial da Meta (seção 3A) | Opção padrão do projeto |
| `twilio` | **Twilio Sandbox** (seção 3B) | Alternativa de configuração mais rápida |

### 3A. WhatsApp Cloud API (Meta) — oficial e gratuita para testes

1. Acesse https://developers.facebook.com e entre com sua conta do Facebook. Se for o primeiro acesso, aceite os termos e confirme que é desenvolvedor.
2. Clique em **Meus apps › Criar app**. Escolha o caso de uso **Outro** e o tipo **Empresa** (Business), e dê um nome, por exemplo "Oráculo".
3. No painel do app, encontre o produto **WhatsApp** e clique em **Configurar**. Se pedir um portfólio empresarial (conta do Meta Business), crie um com o nome do projeto.
4. Abra **WhatsApp › Configuração da API** (API Setup). A página mostra:
   - o **número de teste** no campo **De** (From) → `META_WHATSAPP_NUMERO` (do jeito que aparece, ex.: `+1 555 123 4567`);
   - o **Phone number ID** (identificação do número de telefone) → `META_WHATSAPP_PHONE_NUMBER_ID`;
   - um **token de acesso temporário** → `META_WHATSAPP_TOKEN` (vale **24 horas**; veja o passo 7 para um token que não expira).
5. No campo **Para** (To), clique em **Gerenciar lista de números** e adicione o seu celular. A Meta envia um código pelo WhatsApp para confirmar. Repita para cada celular que for receber mensagens (até 5 no número de teste).
6. **Pelo seu celular**, mande um **Oi** para o número de teste. O WhatsApp só deixa o Oráculo enviar mensagens livres (com os links e vídeos) até 24 horas depois da última mensagem da pessoa; depois disso, mande outro "Oi".
7. **Token que não expira** (recomendado para a apresentação): acesse https://business.facebook.com › **Configurações** › **Usuários do sistema** › **Adicionar** (função Administrador). Em **Atribuir ativos**, dê controle total do app e da conta do WhatsApp. Depois clique em **Gerar token**, escolha o app, a validade **Nunca** e as permissões `whatsapp_business_messaging` e `whatsapp_business_management`. Use esse token em `META_WHATSAPP_TOKEN`.
8. Confira se o `backend/.env` está com `PROVEDOR_WHATSAPP=meta` e salve.

> **Números brasileiros:** o WhatsApp identifica muitos celulares sem o 9 extra. Se a Meta disser que o número não está na lista de teste, o Oráculo tenta de novo automaticamente sem o 9. Se ainda assim falhar, cadastre o número na lista do passo 5 sem o 9 (ex.: `+55 51 9999-8888`).

### 3B. Twilio Sandbox (alternativa)

Envia a mensagem com a resposta, os sites e os vídeos. No ambiente de teste (Sandbox), é gratuito. Para usar a Twilio, coloque `PROVEDOR_WHATSAPP=twilio` no `backend/.env`.

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
