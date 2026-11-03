# Configuração dos serviços externos

O Oráculo usa três serviços gratuitos: o **Supabase** (banco de dados), o **Google Gemini** (IA) e uma **automação no n8n** para o WhatsApp. As chaves ficam nos arquivos `backend/.env` e `automacao/.env`, que **nunca** vão para o GitHub.

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

## 3. WhatsApp com n8n e Evolution API (gratuito, no seu computador)

O Oráculo envia o WhatsApp por uma **automação no n8n**, que roda no seu computador junto com a **Evolution API**, uma ferramenta de código aberto (muito usada no Brasil) que conecta um WhatsApp por **QR code**, como o WhatsApp Web. Tudo é gratuito e já vem configurado na pasta [`automacao/`](../automacao/).

```
Oráculo  ──(pedido: telefone + mensagem)──▶  n8n  ──▶  Evolution API  ──▶  WhatsApp da pessoa
```

O fluxo do n8n confere como o número está registrado no WhatsApp antes de enviar, o que resolve sozinho o "9" extra dos celulares brasileiros.

> **Importante:** a conexão pelo WhatsApp Web **não é um serviço oficial do WhatsApp** e vai contra os termos de uso dele. Para um projeto acadêmico, com poucas mensagens, costuma funcionar bem, mas existe o risco de o número ser bloqueado. **Use um número secundário (um chip só para o Oráculo)**, não o seu WhatsApp principal.

### 3.1. Instalar o Docker Desktop (uma vez só, cerca de 15 minutos)

O Docker roda o n8n, a Evolution API e o banco de dados dela sem instalar cada um separadamente. É gratuito para uso pessoal e educacional.

1. Baixe em https://www.docker.com/products/docker-desktop/ (**Download for Windows**).
2. Execute o instalador e deixe marcada a opção **Use WSL 2**. Aceite os pedidos de permissão do Windows.
3. **Reinicie o computador** quando pedir.
4. Abra o **Docker Desktop**, aceite os termos e pule o login (**Skip**; não precisa de conta).
5. Se aparecer um aviso sobre o **WSL**, clique no botão de atualizar que o próprio Docker mostra e reinicie de novo.
6. Espere aparecer **"Engine running"** (motor em execução) no canto inferior do Docker Desktop.

### 3.2. Ligar a automação

1. Abra a pasta do projeto, entre em `automacao` e dê dois cliques em **`iniciar-automacao.bat`**.
2. Na primeira vez, o download leva alguns minutos. No fim, o navegador abre duas páginas:
   - **n8n**: http://localhost:5678
   - **Evolution API**: http://localhost:8080/manager
3. As senhas já estão no arquivo `automacao/.env`, e o Oráculo (`backend/.env`) já está ligado ao n8n.
4. No **Docker Desktop**, em **Containers**, devem aparecer três itens rodando (bolinha verde): `oraculo-n8n`, `oraculo-evolution` e `oraculo-evolution-db`.

### 3.3. Conectar o WhatsApp na Evolution API (QR code)

1. Na página da Evolution API (http://localhost:8080/manager), faça o login:
   - **Server URL:** `http://localhost:8080`
   - **API Key Global:** o valor da linha `EVOLUTION_API_KEY` do arquivo `automacao/.env` (abra com o Bloco de Notas e copie só o que vem depois do `=`).
2. Clique em **Instance +** (nova instância) e preencha:
   - **Name:** `oraculo` (exatamente assim, em minúsculas; é o nome que o fluxo do n8n usa);
   - **Channel:** `Baileys`;
   - deixe o **Token** como está e clique em **Save**.
3. Abra a instância **oraculo** (ícone de engrenagem ou clique no nome) e clique em **Get QR Code** (gerar QR code).
4. No celular com o **número do Oráculo**: WhatsApp › **Configurações › Aparelhos conectados › Conectar um aparelho** e leia o QR code.
5. Espere a instância aparecer como **Connected** / **open** (conectada). A conexão fica salva: não é preciso ler o QR code de novo a cada vez.

> **O QR code não aparece?** É um problema conhecido quando o WhatsApp atualiza o WhatsApp Web. Consulte a versão atual em https://wppconnect.io/pt-BR/whatsapp-versions/ (a primeira da lista, por exemplo `2.3000.10xxxxxxxx`), coloque-a na linha `WHATSAPP_WEB_VERSAO=` do `automacao/.env`, salve, rode `iniciar-automacao.bat` de novo e repita o passo 3.

### 3.4. Importar o fluxo no n8n

1. Na página do n8n (http://localhost:5678), crie a sua conta local (nome, e-mail e senha; fica só no seu computador). Se oferecer um questionário ou plano pago, pule.
2. Clique em **Create workflow** (ou **+** › Workflow).
3. No menu **⋯** (três pontinhos, no canto superior direito), escolha **Import from File** e selecione `automacao/fluxo-oraculo-whatsapp.json`.
4. Clique em **Save** e ligue a chave **Active** (ou **Publish**) no topo. Sem isso, o Oráculo recebe o erro "O fluxo do n8n não está ativo".

### 3.5. Testar

1. Abra o Oráculo (`iniciar.bat`), faça uma pergunta e clique em **"Quer saber mais sobre o assunto?" › Sim**.
2. Entre ou crie a conta com o seu WhatsApp e clique em **Receber no WhatsApp**.
3. A mensagem chega vinda do número conectado na Evolution API.
4. Se algo falhar, abra o n8n › **Executions**: cada pedido do Oráculo aparece ali, com o passo que deu erro e a explicação.

| Mensagem no Oráculo | O que fazer |
| --- | --- |
| "Não foi possível falar com o n8n" | Abra o Docker Desktop e rode `iniciar-automacao.bat` de novo |
| "O fluxo do n8n não está ativo" | No n8n, abra o fluxo e ligue a chave **Active** |
| "Este número não tem WhatsApp" | Confira o número cadastrado na conta |
| Erro na etapa "Conferir número" no n8n | Na Evolution API, confira se a instância `oraculo` existe e está **conectada**; se não, gere o QR code de novo |

## 4. Conferir

Reinicie o backend e faça uma pergunta na tela. Se aparecer "O serviço ainda não foi configurado", alguma variável do `backend/.env` está vazia: o nome dela aparece no terminal do backend.
