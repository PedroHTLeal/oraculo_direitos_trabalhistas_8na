# Configuração dos serviços externos

O Oráculo usa três serviços gratuitos: o **Supabase** (banco de dados), o **Google Gemini** (IA) e o **Gmail** (envio de e-mails). As chaves ficam no arquivo `backend/.env`, que **nunca** vai para o GitHub.

Antes de começar, copie o modelo:

```bash
cp backend/.env.example backend/.env
```

## 1. Supabase (banco de dados)

Guarda a cartilha do TRT4, as perguntas feitas, as contas e os pedidos de conteúdo por e-mail.

1. Crie uma conta em https://supabase.com e clique em **New project** (plano gratuito).
2. Escolha um nome (ex.: `oraculo`), uma senha para o banco e a região **South America (São Paulo)**.
3. Quando o projeto estiver pronto, abra **SQL Editor** e execute, nesta ordem, cada arquivo da pasta [`supabase/`](../supabase/) (cole todo o conteúdo e clique em **Run**):
   1. [`001_estrutura_inicial.sql`](../supabase/001_estrutura_inicial.sql)
   2. [`002_corrige_busca_e_sinonimos.sql`](../supabase/002_corrige_busca_e_sinonimos.sql)
   3. [`003_modelo_relacional.sql`](../supabase/003_modelo_relacional.sql)
   4. [`004_conta_com_whatsapp.sql`](../supabase/004_conta_com_whatsapp.sql)
   5. [`005_historico_de_operacoes.sql`](../supabase/005_historico_de_operacoes.sql)
   6. [`006_contato_por_email.sql`](../supabase/006_contato_por_email.sql)
   7. [`007_materiais_complementares.sql`](../supabase/007_materiais_complementares.sql)
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

Gera as respostas a partir dos trechos da cartilha. O plano gratuito não pede cartão de crédito.

1. Acesse https://aistudio.google.com e entre com uma conta Google.
2. Aceite os termos de uso, se aparecerem.
3. Clique em **Get API key** (ou **Criar chave de API**) e depois em **Create API key**. Se pedir um projeto, deixe o Google criar um novo.
4. Copie a chave (começa com `AIza`) para `GEMINI_API_KEY`.

> O plano gratuito tem limites diários de uso, suficientes para testes e para a apresentação. Nesse plano, o Google pode usar o conteúdo das requisições para melhorar seus produtos; por isso, o Oráculo envia à IA apenas a pergunta e os trechos da cartilha, nunca o nome ou o e-mail de quem pediu.

## 3. E-mail pelo Gmail (gratuito)

O Oráculo envia por e-mail a resposta, os 2 sites e os 2 vídeos do "Saber mais" e as novidades dos temas acompanhados. O envio usa uma conta do Gmail com uma **senha de app**: uma senha própria para o Oráculo, diferente da senha normal da conta, que pode ser apagada a qualquer momento.

1. Entre na conta Google que vai enviar os e-mails. O ideal é criar uma conta só para o Oráculo (por exemplo, `oraculo.trabalhista.8na@gmail.com`).
2. Ative a **verificação em duas etapas** em https://myaccount.google.com/signinoptions/twosv (o Google só libera a senha de app com ela ativa).
3. Abra https://myaccount.google.com/apppasswords, digite o nome `Oraculo` e clique em **Criar**.
4. O Google mostra uma senha de 16 letras (em quatro blocos). Ela aparece **uma vez só**: copie na hora.
5. No `backend/.env`, preencha:
   - `EMAIL_REMETENTE` → o endereço do Gmail que vai enviar;
   - `EMAIL_SENHA_APP` → a senha de 16 letras (pode colar com ou sem os espaços).
6. Salve o arquivo e reinicie o Oráculo (`iniciar.bat`).

> O Gmail gratuito envia até cerca de 500 e-mails por dia, mais que suficiente para testes e para a apresentação. Para evitar abuso, o Oráculo aceita até 5 pedidos de "Saber mais" por e-mail a cada hora.

**Testar:** faça uma pergunta, clique em **"Quer saber mais sobre o assunto?" › Sim**, informe seu nome e e-mail, marque a autorização e clique em **Receber por e-mail**. Em até 1 minuto o e-mail chega. Na primeira vez, confira também a pasta de **spam** e marque como "Não é spam".

| Mensagem no Oráculo | O que fazer |
| --- | --- |
| "O serviço ainda não foi configurado" | `EMAIL_REMETENTE` ou `EMAIL_SENHA_APP` estão vazios no `backend/.env` |
| "Não conseguimos enviar o e-mail agora" | Veja o terminal do backend. Se aparecer "O Gmail recusou o login", gere uma nova senha de app e confira se a verificação em duas etapas está ativa |
| "Você fez muitos pedidos na última hora" | Limite de 5 pedidos por e-mail por hora; espere e tente de novo |

## 4. Sites e vídeos do "Saber mais"

Os sites e vídeos enviados por e-mail são **escolhidos pela equipe**, sem pesquisa automática. Eles ficam na tabela `materiais_complementares` do Supabase, por assunto, cada um com as palavras-chave que o identificam na pergunta (por exemplo, `ferias` ou `13` e `decimo terceiro`, sempre sem acento e em minúsculas).

- **Pergunta de um assunto cadastrado:** vão os sites e vídeos da equipe; se faltar um site, entra a página da cartilha do TRT4 sobre o tema.
- **Outros assuntos:** vão a página da cartilha do TRT4 sobre o tema, o texto oficial da lei (CLT ou a lei própria do tema, no site do Planalto) e uma busca pronta no YouTube.

Para incluir ou alterar um assunto, entre no painel como curador ou administrador e abra **Sites e vídeos › + Novo link**. Os sinônimos da busca (palavras do dia a dia traduzidas para os termos da cartilha) ficam em **Sinônimos da busca**.

## 5. Conferir

Reinicie o backend e faça uma pergunta na tela. Se aparecer "O serviço ainda não foi configurado", alguma variável do `backend/.env` está vazia: o nome dela aparece no terminal do backend.
