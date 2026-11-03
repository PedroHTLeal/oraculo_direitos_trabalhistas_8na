# Publicação na internet (Vercel, gratuita)

O Oráculo fica disponível em um endereço público (por exemplo, `https://oraculo-8na.vercel.app`), sem custo, pela **Vercel**. Ela publica o site (React) e o backend (Python/FastAPI) a partir do próprio repositório do GitHub e atualiza tudo sozinha a cada envio para o `main`.

| Opção | Serve para o Oráculo? | Por quê |
| --- | --- | --- |
| **Vercel (plano Hobby)** | **Sim** | Gratuita para projetos pessoais e acadêmicos, roda o site e o backend Python juntos, guarda as chaves com segurança e permite enviar e-mail pelo Gmail |
| GitHub Pages (github.io) | Não | Só hospeda páginas estáticas: não roda o backend em Python, então não haveria respostas da IA, login nem envio de e-mail. Também não guarda chaves em segredo |

O projeto já vem preparado: [`vercel.json`](../vercel.json) (como montar o site e o backend), [`api/index.py`](../api/index.py) (entrada do backend) e [`requirements.txt`](../requirements.txt) (dependências do Python).

## Passo a passo (cerca de 10 minutos)

### 1. Criar a conta na Vercel

1. Acesse https://vercel.com/signup.
2. Escolha **Hobby** (gratuito) e informe seu nome.
3. Clique em **Continue with GitHub** e entre com a conta dona do repositório.
4. Autorize a Vercel no GitHub. Se perguntar quais repositórios liberar, escolha **Only select repositories** e marque `oraculo_direitos_trabalhistas_8na`.

### 2. Importar o projeto

1. No painel da Vercel, clique em **Add New… › Project**.
2. Ao lado de `oraculo_direitos_trabalhistas_8na`, clique em **Import**.
3. Na tela **Configure Project**:
   - **Project Name:** por exemplo `oraculo-8na` (vira o endereço `oraculo-8na.vercel.app`);
   - **Framework Preset:** `Other`;
   - **Root Directory:** deixe `./`;
   - **Build and Output Settings:** não mexa; as configurações vêm do `vercel.json`.

### 3. Colocar as chaves (Environment Variables)

Ainda na tela **Configure Project**, abra **Environment Variables** e cadastre uma por uma, copiando os valores do seu `backend/.env` (abra com o Bloco de Notas e copie só o que vem depois do `=`):

| Name | De onde vem |
| --- | --- |
| `SUPABASE_URL` | `backend/.env` |
| `SUPABASE_SERVICE_ROLE_KEY` | `backend/.env` |
| `GEMINI_API_KEY` | `backend/.env` |
| `EMAIL_REMETENTE` | `backend/.env` |
| `EMAIL_SENHA_APP` | `backend/.env` |

> As chaves ficam guardadas só na Vercel, sem aparecer no site nem no GitHub. Nunca as coloque em arquivos do repositório.

### 4. Publicar

1. Clique em **Deploy** e espere de 1 a 3 minutos.
2. Quando aparecer **Congratulations!**, clique em **Continue to Dashboard** e depois em **Visit**.

### 5. Conferir

1. Abra `https://SEU-ENDERECO.vercel.app/api/saude`: deve aparecer `{"status":"ok"}`.
2. Abra o endereço principal, faça uma pergunta e confira a resposta.
3. Clique em **"Quer saber mais sobre o assunto?" › Sim**, informe nome e e-mail e confira se o e-mail chega.
4. Entre em **Entrar** com uma conta da equipe e confira o painel.

## Depois de publicado

- **Atualizações:** cada `git push` no `main` publica uma versão nova sozinho, em 1 a 3 minutos. O andamento aparece em **Deployments**.
- **Trocar uma chave:** **Settings › Environment Variables**, edite o valor e depois, em **Deployments**, clique em **⋯ › Redeploy** na versão mais recente.
- **Mostrar à professora:** basta enviar o endereço. Para ela ver o painel, crie uma conta de curador ou administrador em **Usuários**.

| Problema | O que fazer |
| --- | --- |
| "O serviço ainda não foi configurado" | Falta uma variável do passo 3: cadastre e faça **Redeploy** |
| Erro 500 ou página da API não encontrada | Em **Deployments**, abra a versão e veja **Logs**; a mensagem diz o que falhou |
| O e-mail não chega | Confira `EMAIL_REMETENTE` e `EMAIL_SENHA_APP` na Vercel e a pasta de spam |
| A primeira pergunta demora alguns segundos a mais | É normal: a função "acorda" depois de um tempo parada |

> No plano gratuito, o backend roda como funções que "dormem" entre os acessos. Por isso, na Vercel o e-mail do "Saber mais" é enviado dentro do próprio pedido, e a tela leva alguns segundos a mais para confirmar o envio.
