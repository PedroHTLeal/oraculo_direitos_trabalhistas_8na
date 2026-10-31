"""Extrai a Cartilha de Direitos e Obrigações no Trabalho do TRT4 para JSON.

Cada tema da cartilha é uma página; o texto é dividido em trechos por
subtítulo, que são as unidades usadas na busca.

Uso (na pasta backend/):
    python scripts/extrair_cartilha.py
"""

import json
import re
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup

URL_INDICE = "https://www.trt4.jus.br/portais/trt4/cartilha-de-direitos-e-obrigacoes-no-trabalho"
ARQUIVO_SAIDA = Path(__file__).resolve().parent.parent / "dados" / "cartilha.json"
CABECALHOS = {"User-Agent": "Mozilla/5.0 (Oraculo dos Direitos Trabalhistas - projeto academico)"}
TAMANHO_MAXIMO_TRECHO = 1500


def baixar(url):
    resposta = requests.get(url, headers=CABECALHOS, timeout=30)
    resposta.raise_for_status()
    resposta.encoding = "utf-8"
    return BeautifulSoup(resposta.text, "html.parser")


def listar_temas():
    pagina = baixar(URL_INDICE)
    temas = []
    for link in pagina.find("main").find_all("a", href=True):
        # O nome do tema fica no <strong>; o restante do link é o ícone
        nome = link.find("strong")
        titulo = limpar(nome.get_text(" ")) if nome else ""
        if "/portais/trt4/" in link["href"] and titulo:
            temas.append({"tema": titulo, "url": requests.compat.urljoin(URL_INDICE, link["href"])})
    return temas


def limpar(texto):
    return re.sub(r"\s+", " ", texto).strip()


TITULOS = ["h2", "h3", "h4"]
BLOCOS = ["p", "li", "tr", "div"]
CONTEINERES = TITULOS + ["p", "li", "ul", "ol", "table", "div"]


def eh_bloco_de_texto(elemento):
    # Divs só contam quando têm texto direto, sem outros blocos dentro
    if elemento.name == "div" and elemento.find(CONTEINERES):
        return False
    # Evita ler duas vezes o texto de um bloco que está dentro de outro
    return not elemento.find_parent(["li", "tr", "p"])


def extrair_secoes(url, tema):
    conteudo = baixar(url).find("div", class_="ancora")
    for icone in conteudo.find_all("svg"):
        icone.decompose()
    secoes = [{"secao": "Visão geral", "blocos": []}]

    for elemento in conteudo.find_all(TITULOS + BLOCOS):
        if elemento.name in BLOCOS and not eh_bloco_de_texto(elemento):
            continue
        if elemento.name == "tr":
            celulas = [limpar(c.get_text(" ")) for c in elemento.find_all(["th", "td"])]
            texto = " | ".join(c for c in celulas if c)
        else:
            texto = limpar(elemento.get_text(" "))
        if not texto or texto.startswith("<") or texto.lower() == tema.lower():
            continue
        if elemento.name in TITULOS:
            secoes.append({"secao": texto, "blocos": []})
        else:
            secoes[-1]["blocos"].append(("- " if elemento.name == "li" else "") + texto)

    return [s for s in secoes if s["blocos"]]


def dividir_em_trechos(blocos):
    trechos, atual = [], ""
    for bloco in blocos:
        if atual and len(atual) + len(bloco) > TAMANHO_MAXIMO_TRECHO:
            trechos.append(atual)
            atual = ""
        atual = f"{atual}\n{bloco}" if atual else bloco
    if atual:
        trechos.append(atual)
    return trechos


def main():
    temas = listar_temas()
    registros = []
    for item in temas:
        # A ordem é contada no tema inteiro (url + ordem identifica o trecho)
        ordem = 0
        for secao in extrair_secoes(item["url"], item["tema"]):
            for texto in dividir_em_trechos(secao["blocos"]):
                ordem += 1
                registros.append(
                    {
                        "tema": item["tema"],
                        "secao": secao["secao"],
                        "ordem": ordem,
                        "texto": texto,
                        "url": item["url"],
                    }
                )
        print(f"{item['tema']}: ok")
        time.sleep(1)  # evita sobrecarregar o site do TRT4

    ARQUIVO_SAIDA.parent.mkdir(exist_ok=True)
    ARQUIVO_SAIDA.write_text(json.dumps(registros, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{len(registros)} trechos de {len(temas)} temas salvos em {ARQUIVO_SAIDA}")


if __name__ == "__main__":
    main()
