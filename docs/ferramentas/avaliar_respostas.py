"""Avaliação das respostas da IA (PB12, RNF08) com o banco e o Gemini reais.

Faz um conjunto fixo de perguntas de referência, sem gravar nada no banco, e confere:
- se a IA respondeu quando a cartilha trata do assunto e recusou quando não trata (RF09);
- se as fontes citadas são do tema esperado da cartilha (RF07, RNF08);
- se as fontes citadas vieram mesmo da busca (a IA não pode inventar trechos);
- se a resposta é curta, em até 3 parágrafos (RF06).

O resultado é gravado em docs/avaliacao-ia.md.

Uso (na raiz do projeto, com o backend/.env preenchido):
    backend\\.venv\\Scripts\\python docs\\ferramentas\\avaliar_respostas.py
"""

import json
import sys
import time
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "backend"))

from google.genai import errors  # noqa: E402

from app.config import carregar_configuracao  # noqa: E402
from app.ia import AssistenteIA, RecusaDaIA  # noqa: E402
from app.repositorio import RepositorioSupabase  # noqa: E402

SAIDA = RAIZ / "docs" / "avaliacao-ia.md"
# Resultados já obtidos, para continuar de onde parou quando acaba a cota diária
PROGRESSO = RAIZ / "docs" / "ferramentas" / "avaliacao-progresso.json"
PAUSA = 5  # segundos entre perguntas, para respeitar o limite do plano gratuito
LIMITE_CARACTERES = 1200

# (pergunta, temas da cartilha aceitos como fonte; vazio = a cartilha não trata do assunto)
CASOS = [
    ("Quantos dias de férias eu tenho direito?", {"Férias"}),
    ("Posso vender parte das minhas férias?", {"Férias"}),
    ("Quando o 13º salário deve ser pago?", {"Salário e Remuneração"}),
    ("Quem trabalhou só alguns meses recebe 13º?", {"Salário e Remuneração", "Rescisão (término)"}),
    ("Qual é a jornada máxima de trabalho por dia?", {"Jornada de Trabalho"}),
    ("Como funciona o pagamento de horas extras?", {"Jornada de Trabalho", "Salário e Remuneração"}),
    ("O que recebo se for demitido sem justa causa?", {"Rescisão (término)"}),
    ("Quanto tempo de aviso prévio eu preciso cumprir?", {"Rescisão (término)"}),
    ("Estagiário tem direito a férias?", {"Contrato de Estágio"}),
    ("Qual é a carga horária máxima de um estágio?", {"Contrato de Estágio"}),
    ("Empregada doméstica tem direito a FGTS?", {"Fundo de Garantia", "Relação de Emprego", "Contratações e modalidades"}),
    ("Diarista tem carteira assinada?", {"Relação de Emprego", "Contratações e modalidades"}),
    ("Qual é a capital da França?", set()),
    ("Qual é a melhor receita de bolo de cenoura?", set()),
    ("Como declarar o imposto de renda de uma empresa no exterior?", set()),
]


def avaliar(repositorio, ia, pergunta, temas_esperados):
    trechos = repositorio.buscar_trechos(pergunta)
    inicio = time.time()
    resultado = {"encontrou": False, "resposta": "", "trechos_usados": []}
    for tentativa in range(4):
        try:
            if trechos:
                resultado = ia.responder(pergunta, trechos)
            break
        except RecusaDaIA:
            break
        except errors.ServerError:
            # Os dois modelos do plano gratuito sobrecarregados: espera e tenta de novo
            if tentativa == 3:
                raise
            time.sleep(30)
    segundos = time.time() - inicio
    por_id = {t["id"]: t for t in trechos}
    citados = resultado["trechos_usados"] if resultado["encontrou"] else []
    inventados = [i for i in citados if i not in por_id]
    temas = sorted({por_id[i]["tema"] for i in citados if i in por_id})
    paragrafos = [p for p in resultado["resposta"].split("\n\n") if p.strip()]

    deve_responder = bool(temas_esperados)
    criterios = {
        "Respondeu quando devia": resultado["encontrou"] == deve_responder,
        "Fonte do tema certo": (not deve_responder) or bool(set(temas) & temas_esperados),
        "Sem fontes inventadas": not inventados,
        "Resposta curta": len(resultado["resposta"]) <= LIMITE_CARACTERES and len(paragrafos) <= 3,
    }
    return {
        "pergunta": pergunta,
        "esperado": ", ".join(sorted(temas_esperados)) or "Fora da cartilha",
        "encontrou": resultado["encontrou"],
        "temas": ", ".join(temas) or "—",
        "segundos": segundos,
        "criterios": criterios,
        "aprovado": all(criterios.values()),
    }


def escrever(resultados):
    feitos = [r for r in resultados if r]
    aprovados = sum(r["aprovado"] for r in feitos)
    pendentes = len(CASOS) - len(feitos)
    resumo = f"{aprovados} de {len(feitos)} perguntas avaliadas aprovadas em todos os critérios"
    if pendentes:
        resumo += f" ({pendentes} ainda não avaliadas: limite diário do plano gratuito)"
    linhas = [
        "# Avaliação das respostas da IA",
        "",
        f"**Data:** {datetime.now():%d/%m/%Y} · **Modelo:** Google Gemini (plano gratuito) · **Resultado:** {resumo}",
        "",
        "Avaliação do item PB12 do backlog e do RNF08: perguntas de referência feitas ao sistema real (banco no Supabase e IA), "
        "sem gravar nada no banco. Gerada por [`docs/ferramentas/avaliar_respostas.py`](ferramentas/avaliar_respostas.py).",
        "",
        "## Critérios",
        "",
        "| Critério | O que confere | Requisito |",
        "| --- | --- | --- |",
        "| Respondeu quando devia | Responde as perguntas que a cartilha trata e recusa as que ela não trata | RF09 |",
        "| Fonte do tema certo | Pelo menos uma fonte citada é do tema esperado da cartilha | RF07, RNF08 |",
        "| Sem fontes inventadas | Todo trecho citado pela IA veio da busca no banco | RNF08 |",
        f"| Resposta curta | Até {LIMITE_CARACTERES} caracteres e até 3 parágrafos | RF06 |",
        "",
        "## Resultado por pergunta",
        "",
        "| Pergunta | Tema esperado | Respondeu? | Temas das fontes | Critérios |",
        "| --- | --- | --- | --- | --- |",
    ]
    for (pergunta, temas), r in zip(CASOS, resultados):
        if not r:
            esperado = ", ".join(sorted(temas)) or "Fora da cartilha"
            linhas.append(f"| {pergunta} | {esperado} | — | — | Pendente (limite diário do plano gratuito) |")
            continue
        falhas = [nome for nome, ok in r["criterios"].items() if not ok]
        situacao = "Aprovada" if r["aprovado"] else "Falhou: " + "; ".join(falhas)
        linhas.append(f"| {r['pergunta']} | {r['esperado']} | {'Sim' if r['encontrou'] else 'Não'} | {r['temas']} | {situacao} |")
    linhas += [
        "",
        "## Observações",
        "",
        "- O plano gratuito do Gemini permite 20 pedidos por dia no modelo principal. Quando ele está sobrecarregado ou sem cota, "
        "o sistema usa o modelo reserva (com cota própria), e cada resposta pode levar de 10 a 25 segundos (RNF05).",
        "- O sistema também descarta, antes de mostrar a resposta, qualquer trecho citado que não tenha vindo da busca.",
        "- Perguntas fora da cartilha, como \"Qual é a capital da França?\", também foram testadas no sistema real no caso CT27 da Sprint 09.",
        "",
    ]
    SAIDA.write_text("\n".join(linhas), encoding="utf-8")


def main():
    """Avalia as perguntas que faltam; o progresso fica guardado para continuar no dia seguinte."""
    config = carregar_configuracao()
    repositorio = RepositorioSupabase(config.supabase_url, config.supabase_chave_servico)
    ia = AssistenteIA()
    feitos = json.loads(PROGRESSO.read_text(encoding="utf-8")) if PROGRESSO.exists() else {}
    for pergunta, temas in CASOS:
        if pergunta in feitos:
            continue
        try:
            resultado = avaliar(repositorio, ia, pergunta, temas)
        except errors.ClientError as erro:
            if erro.code != 429:
                raise
            print("Limite diário do plano gratuito atingido; rode de novo amanhã para continuar.")
            break
        print(("OK   " if resultado["aprovado"] else "FALHA"), pergunta, "|", resultado["temas"], flush=True)
        feitos[pergunta] = resultado
        PROGRESSO.write_text(json.dumps(feitos, ensure_ascii=False, indent=1), encoding="utf-8")
        time.sleep(PAUSA)
    escrever([feitos.get(pergunta) for pergunta, _ in CASOS])
    print("Gravado em", SAIDA)


if __name__ == "__main__":
    main()
