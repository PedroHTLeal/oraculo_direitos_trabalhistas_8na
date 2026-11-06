"""Reordenação dos trechos encontrados, dando mais peso às palavras raras da pergunta.

A busca do banco (PostgreSQL) encontra os trechos candidatos, mas ordena contando
quantas vezes as palavras aparecem, sem considerar se a palavra é comum ou rara na
cartilha. Em "Diarista tem carteira assinada?", as palavras comuns "carteira" e
"assinada" puxavam outros trechos para cima e o trecho sobre diaristas ficava em 32º.

Aqui cada palavra vale mais quanto mais rara ela é na cartilha (IDF, a mesma ideia
usada por buscadores), e conta em dobro quando aparece no tema ou no subtítulo.
"""

import math
import re

from app.materiais import normalizar

TAMANHO_DA_RAIZ = 5  # "diarista" e "diaristas" viram "diari"; "assinada" e "assinatura", "assin"

# Palavras que não ajudam a encontrar o assunto
PALAVRAS_VAZIAS = {
    "que", "com", "por", "para", "uma", "uns", "umas", "sao", "ser", "tem", "ter", "tenho", "temos", "pode", "posso",
    "qual", "quais", "quando", "como", "onde", "quem", "quanto", "quanta", "quantos", "quantas", "meu", "minha", "meus",
    "minhas", "seu", "sua", "seus", "suas", "isso", "esse", "essa", "este", "esta", "mais", "muito", "sobre", "dos",
    "das", "nos", "nas", "pelo", "pela", "tambem", "ainda", "voce", "deve", "fazer", "foi", "sim", "nao", "direito",
    "direitos", "trabalho",
}


def raizes(texto):
    """Raízes das palavras relevantes do texto, sem acentos e sem palavras vazias."""
    palavras = re.findall(r"[a-z0-9]+", normalizar(texto))
    return {p[:TAMANHO_DA_RAIZ] for p in palavras if len(p) > 2 and p not in PALAVRAS_VAZIAS}


class Corpus:
    """Frequência de cada raiz na cartilha inteira, para saber o quanto cada palavra é rara."""

    def __init__(self, trechos):
        self.total = len(trechos)
        self.frequencia = {}
        for trecho in trechos:
            for raiz in raizes(f"{trecho['tema']} {trecho['secao']} {trecho['texto']}"):
                self.frequencia[raiz] = self.frequencia.get(raiz, 0) + 1

    def peso(self, raiz):
        return math.log((self.total + 1) / (self.frequencia.get(raiz, 0) + 0.5))


def expandir(pergunta, sinonimos):
    """Acrescenta à pergunta os termos da cartilha dos sinônimos encontrados nela."""
    texto = normalizar(pergunta)
    extras = [s["equivalentes"] for s in sinonimos if re.search(rf"\b{re.escape(s['termo'])}\b", texto)]
    return " ".join([pergunta, *extras])


def reordenar(pergunta, candidatos, corpus, sinonimos=()):
    """Ordena os candidatos pela soma dos pesos das palavras da pergunta que cada um contém."""
    procuradas = raizes(expandir(pergunta, sinonimos))

    def pontuacao(trecho):
        titulo = raizes(f"{trecho['tema']} {trecho['secao']}")
        conteudo = titulo | raizes(trecho["texto"])
        pontos = sum(corpus.peso(r) * (2 if r in titulo else 1) for r in procuradas if r in conteudo)
        # Em caso de empate, vale a ordem da busca do banco
        return pontos, trecho.get("relevancia") or 0

    return sorted(candidatos, key=pontuacao, reverse=True)
