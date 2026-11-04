# Avaliação das respostas da IA

**Data:** 04/11/2026 · **Modelo:** Google Gemini (plano gratuito) · **Resultado:** 9 de 9 perguntas avaliadas aprovadas em todos os critérios (6 ainda não avaliadas: limite diário do plano gratuito)

Avaliação do item PB12 do backlog e do RNF08: perguntas de referência feitas ao sistema real (banco no Supabase e IA), sem gravar nada no banco. Gerada por [`docs/ferramentas/avaliar_respostas.py`](ferramentas/avaliar_respostas.py).

## Critérios

| Critério | O que confere | Requisito |
| --- | --- | --- |
| Respondeu quando devia | Responde as perguntas que a cartilha trata e recusa as que ela não trata | RF09 |
| Fonte do tema certo | Pelo menos uma fonte citada é do tema esperado da cartilha | RF07, RNF08 |
| Sem fontes inventadas | Todo trecho citado pela IA veio da busca no banco | RNF08 |
| Resposta curta | Até 1200 caracteres e até 3 parágrafos | RF06 |

## Resultado por pergunta

| Pergunta | Tema esperado | Respondeu? | Temas das fontes | Critérios |
| --- | --- | --- | --- | --- |
| Quantos dias de férias eu tenho direito? | Férias | Sim | Férias | Aprovada |
| Posso vender parte das minhas férias? | Férias | Sim | Férias | Aprovada |
| Quando o 13º salário deve ser pago? | Salário e Remuneração | Sim | Salário e Remuneração | Aprovada |
| Quem trabalhou só alguns meses recebe 13º? | Rescisão (término), Salário e Remuneração | Sim | Salário e Remuneração | Aprovada |
| Qual é a jornada máxima de trabalho por dia? | Jornada de Trabalho | Sim | Jornada de Trabalho, Salário e Remuneração | Aprovada |
| Como funciona o pagamento de horas extras? | Jornada de Trabalho, Salário e Remuneração | Sim | Jornada de Trabalho, Salário e Remuneração | Aprovada |
| O que recebo se for demitido sem justa causa? | Rescisão (término) | Sim | Rescisão (término) | Aprovada |
| Quanto tempo de aviso prévio eu preciso cumprir? | Rescisão (término) | Sim | Rescisão (término) | Aprovada |
| Estagiário tem direito a férias? | Contrato de Estágio | Sim | Contrato de Estágio | Aprovada |
| Qual é a carga horária máxima de um estágio? | Contrato de Estágio | — | — | Pendente (limite diário do plano gratuito) |
| Empregada doméstica tem direito a FGTS? | Contratações e modalidades, Fundo de Garantia, Relação de Emprego | — | — | Pendente (limite diário do plano gratuito) |
| Diarista tem carteira assinada? | Contratações e modalidades, Relação de Emprego | — | — | Pendente (limite diário do plano gratuito) |
| Qual é a capital da França? | Fora da cartilha | — | — | Pendente (limite diário do plano gratuito) |
| Qual é a melhor receita de bolo de cenoura? | Fora da cartilha | — | — | Pendente (limite diário do plano gratuito) |
| Como declarar o imposto de renda de uma empresa no exterior? | Fora da cartilha | — | — | Pendente (limite diário do plano gratuito) |

## Observações

- O plano gratuito do Gemini permite 20 pedidos por dia no modelo principal. Quando ele está sobrecarregado ou sem cota, o sistema usa o modelo reserva (com cota própria), e cada resposta pode levar de 10 a 25 segundos (RNF05).
- O sistema também descarta, antes de mostrar a resposta, qualquer trecho citado que não tenha vindo da busca.
- Perguntas fora da cartilha, como "Qual é a capital da França?", também foram testadas no sistema real no caso CT27 da Sprint 09.
