"""Sites e vídeos do "Saber mais", escolhidos e conferidos pela equipe (sem pesquisa por API).

Os materiais ficam na tabela materiais_complementares, por assunto. O assunto é
escolhido pelas palavras-chave encontradas na pergunta. Quando nenhum assunto
combina, vão a página da cartilha do TRT4 sobre o tema e o texto da lei.
"""

import re
import unicodedata
import urllib.parse

QUANTIDADE = 2

CLT = ("Consolidação das Leis do Trabalho - CLT (Planalto)", "https://www.planalto.gov.br/ccivil_03/decreto-lei/del5452.htm")

# Lei principal de cada tema da cartilha; os demais temas usam a CLT
LEIS = {
    "Contrato de Estágio": ("Lei do Estágio - Lei nº 11.788/2008 (Planalto)", "https://www.planalto.gov.br/ccivil_03/_ato2007-2010/2008/lei/l11788.htm"),
    "Fundo de Garantia": ("Lei do FGTS - Lei nº 8.036/1990 (Planalto)", "https://www.planalto.gov.br/ccivil_03/leis/l8036consol.htm"),
    "Seguro-Desemprego": ("Lei do Seguro-Desemprego e do Abono - Lei nº 7.998/1990 (Planalto)", "https://www.planalto.gov.br/ccivil_03/leis/l7998.htm"),
    "Abono Salarial": ("Lei do Seguro-Desemprego e do Abono - Lei nº 7.998/1990 (Planalto)", "https://www.planalto.gov.br/ccivil_03/leis/l7998.htm"),
    "Vales Transporte e Alimentação": ("Lei do Vale-Transporte - Lei nº 7.418/1985 (Planalto)", "https://www.planalto.gov.br/ccivil_03/leis/l7418.htm"),
    "Salário Família": ("Lei de Benefícios da Previdência - Lei nº 8.213/1991 (Planalto)", "https://www.planalto.gov.br/ccivil_03/leis/l8213cons.htm"),
    "Pessoas com Deficiência": ("Estatuto da Pessoa com Deficiência - Lei nº 13.146/2015 (Planalto)", "https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2015/lei/l13146.htm"),
    "Trabalho Infantil": ("Estatuto da Criança e do Adolescente - Lei nº 8.069/1990 (Planalto)", "https://www.planalto.gov.br/ccivil_03/leis/l8069.htm"),
}


def normalizar(texto):
    """Minúsculas e sem acentos ("13º Salário" vira "13o salario")."""
    sem_acento = unicodedata.normalize("NFKD", texto or "").encode("ascii", "ignore").decode()
    return sem_acento.lower()


def escolher_assunto(pergunta, cadastrados):
    """Devolve o assunto com mais palavras-chave na pergunta, ou None."""
    texto = normalizar(pergunta)
    pontos = {}
    for material in cadastrados:
        acertos = sum(1 for palavra in material["palavras_chave"] if re.search(rf"\b{re.escape(palavra)}", texto))
        if acertos:
            pontos[material["assunto"]] = max(pontos.get(material["assunto"], 0), acertos)
    return max(pontos, key=pontos.get) if pontos else None


def montar_materiais(pergunta, tema, url_cartilha, cadastrados):
    assunto = escolher_assunto(pergunta, cadastrados)
    escolhidos = sorted((m for m in cadastrados if m["assunto"] == assunto), key=lambda m: m["ordem"])
    sites = [{"titulo": m["titulo"], "url": m["url"]} for m in escolhidos if m["tipo"] == "site"]
    videos = [{"titulo": m["titulo"], "url": m["url"]} for m in escolhidos if m["tipo"] == "video"]

    # Completa os sites com fontes oficiais: a cartilha do TRT4 e a lei do tema
    complementos = []
    if url_cartilha:
        complementos.append({"titulo": f"{tema} - Cartilha de Direitos e Obrigações no Trabalho (TRT4)", "url": url_cartilha})
    titulo_lei, url_lei = LEIS.get(tema, CLT)
    complementos.append({"titulo": titulo_lei, "url": url_lei})
    vistos = {s["url"] for s in sites}
    sites += [c for c in complementos if c["url"] not in vistos]

    if not videos:
        # Sem vídeos escolhidos para o assunto: indica uma busca pronta no YouTube
        videos = [
            {
                "titulo": f"Vídeos sobre {tema} no YouTube",
                "url": "https://www.youtube.com/results?search_query=" + urllib.parse.quote_plus(f"{tema} direitos trabalhistas"),
            }
        ]
    return {"sites": sites[:QUANTIDADE], "videos": videos[:QUANTIDADE]}
