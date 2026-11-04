"""Gera o relatório único de entrega (Sprints 01 a 09) em PDF, no estilo do relatório da Sprint 01.

Junta o relatório da Sprint 01 (docs/sprints/sprint-01/relatorio.md), a página de
cada Sprint, os diagramas da Sprint 02 e o registro de decisões, monta um HTML
com capa e índice e imprime em PDF com o Microsoft Edge (Playwright). Depois
acrescenta o rodapé e a numeração das páginas, como no documento original.

Uso (na raiz do projeto, com o ambiente do backend):
    backend\\.venv\\Scripts\\python docs\\ferramentas\\gerar_relatorio.py

Requer: markdown, pymupdf, pillow e playwright (pip install markdown pymupdf pillow playwright).
"""

import html
import re
import sys
import tempfile
from pathlib import Path

import fitz
import markdown
from PIL import Image
from playwright.sync_api import sync_playwright

RAIZ = Path(__file__).resolve().parents[2]
DOCS = RAIZ / "docs"
FERRAMENTAS = DOCS / "ferramentas"
SAIDA = DOCS / "entrega" / "Oráculo dos Direitos Trabalhistas - 8NA - Sprints 01 a 09.pdf"
GITHUB = "https://github.com/PedroHTLeal/oraculo_direitos_trabalhistas_8na/blob/main/"
RODAPE = ["Tópicos Integradores em Ciência da Computação", "Oráculo dos Direitos Trabalhistas", "Kaleido Void Studios · 8NA"]
SUBTITULO = "Sprints 01 a 09: do planejamento à entrega"

SPRINTS = [DOCS / "sprints" / f"sprint-{n:02d}" / "README.md" for n in range(2, 10)]


def ler(caminho):
    return caminho.read_text(encoding="utf-8")


def converter(texto, origem, pasta_imagens):
    """Markdown → HTML, com links do repositório apontando para o GitHub e imagens locais reduzidas."""

    def link(m):
        rotulo, alvo = m.group(1), m.group(2)
        if alvo.startswith(("http://", "https://", "mailto:")):
            return m.group(0)
        if alvo.startswith("#"):
            return rotulo  # âncora interna: no PDF fica só o texto
        caminho, _, ancora = alvo.partition("#")
        destino = (origem.parent / caminho).resolve()
        try:
            relativo = destino.relative_to(RAIZ).as_posix()
        except ValueError:
            return rotulo
        return f"[{rotulo}]({GITHUB}{relativo}{'#' + ancora if ancora else ''})"

    def imagem(m):
        legenda, alvo = m.group(1), m.group(2)
        arquivo = (origem.parent / alvo).resolve()
        reduzida = pasta_imagens / (arquivo.stem + ".jpg")
        if not reduzida.exists():
            figura = Image.open(arquivo).convert("RGB")
            figura.thumbnail((1400, 1400))
            figura.save(reduzida, quality=82)
        return f'<figure><img src="{reduzida.as_uri()}" alt="{html.escape(legenda)}"><figcaption>{html.escape(legenda)}</figcaption></figure>'

    texto = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", imagem, texto)
    texto = re.sub(r"(?<!!)\[([^\]]+)\]\(([^)]+)\)", link, texto)
    # Diagramas: os blocos mermaid são desenhados no navegador; um título em negrito logo
    # antes do diagrama fica junto dele, para não sobrar sozinho no fim da página
    texto = re.sub(
        r"(?:\*\*([^*\n]+)\*\*\n\n)?```mermaid\n(.*?)```",
        lambda m: (
            '<div class="diagrama">'
            + (f'<p class="diagrama-titulo"><strong>{html.escape(m.group(1))}</strong></p>' if m.group(1) else "")
            + f'<pre class="mermaid">{html.escape(m.group(2))}</pre></div>'
        ),
        texto,
        flags=re.DOTALL,
    )
    return markdown.markdown(texto, extensions=["tables", "fenced_code", "sane_lists"])


def sem_navegacao(texto):
    # Tira os links de volta ao índice, que só fazem sentido no GitHub
    texto = re.sub(r" · \[← Voltar ao índice\]\([^)]+\)", "", texto)
    return re.sub(r"^\[← Voltar[^\n]*\n", "", texto, flags=re.MULTILINE)


def capitulos(pasta_imagens):
    """Devolve [(título no índice, html)] na ordem do relatório."""
    partes = []
    relatorio = DOCS / "sprints" / "sprint-01" / "relatorio.md"
    texto = ler(relatorio)
    corpo, _, historico = texto.partition("## Histórico de alterações")
    corpo = corpo[corpo.index("## 1. Identificação da Equipe"):]
    for bloco in re.split(r"(?=^## \d+\. )", corpo, flags=re.MULTILINE):
        if not bloco.strip():
            continue
        titulo = bloco.splitlines()[0].removeprefix("## ").strip()
        numero, _, nome = titulo.partition(" ")
        conteudo = converter("\n".join(bloco.splitlines()[1:]).replace("\n### ", "\n## "), relatorio, pasta_imagens)
        cabecalho = f'<h1 class="secao"><span class="numero">{numero}</span>{html.escape(nome)}</h1>'
        partes.append((titulo, cabecalho + conteudo, "sprint01"))

    for leia in SPRINTS:
        texto = sem_navegacao(ler(leia))
        titulo = texto.splitlines()[0].removeprefix("# ").strip()
        conteudo = converter("\n".join(texto.splitlines()[1:]), leia, pasta_imagens)
        if leia.parent.name == "sprint-02":
            diagramas = sem_navegacao(ler(leia.parent / "diagramas.md"))
            diagramas = "\n".join(diagramas.splitlines()[1:]).replace("\n## ", "\n### ")
            conteudo += converter("## Diagramas técnicos\n" + diagramas, leia.parent / "diagramas.md", pasta_imagens)
        partes.append((titulo, f'<h1 class="capitulo">{html.escape(titulo)}</h1>{conteudo}', "sprint"))

    # Documentos gerais, depois das Sprints
    for documento in (DOCS / "avaliacao-ia.md", DOCS / "decisoes.md"):
        if not documento.exists():
            continue
        texto = ler(documento)
        titulo = texto.splitlines()[0].removeprefix("# ").strip()
        conteudo = converter("\n".join(texto.splitlines()[1:]), documento, pasta_imagens)
        partes.append((titulo, f'<h1 class="capitulo">{html.escape(titulo)}</h1>{conteudo}', "sprint"))

    partes.append(("Histórico de alterações do relatório", '<h1 class="capitulo">Histórico de alterações do relatório</h1>' + converter(historico, relatorio, pasta_imagens), "sprint"))
    return partes


CSS = """
@page { size: A4; margin: 22mm 20mm 26mm 20mm; }
* { box-sizing: border-box; }
body { margin: 0; font-family: 'PT Serif', Georgia, serif; font-size: 10.5pt; line-height: 1.5; color: #000; }
.capa { height: 249mm; position: relative; page-break-after: always; }
.capa .logo { width: 25mm; margin-top: 6mm; }
.capa .curso { position: absolute; top: 88mm; font-weight: 700; font-size: 15pt; }
.capa .titulo { position: absolute; top: 108mm; font-size: 38pt; line-height: 1.05; font-weight: 400; margin: 0; }
.capa .subtitulo { position: absolute; top: 152mm; font-style: italic; font-size: 15pt; }
.capa .creditos { position: absolute; bottom: 0; font-family: 'PT Sans', Arial, sans-serif; font-size: 11pt; border-collapse: collapse; }
.capa .creditos td { padding: 2px 40px 2px 0; border: none; }
.capa .creditos td:first-child { font-weight: 700; }
.indice { page-break-after: always; }
.indice h1 { text-align: center; font-size: 26pt; margin: 0 0 10mm; }
.indice table { width: 100%; border-collapse: collapse; font-size: 11pt; }
.indice td { padding: 4.5pt 0; border: none; }
.indice td.pagina { width: 18mm; font-weight: 700; }
.indice tr.grupo td { padding-top: 9pt; }
h1.secao { font-size: 25pt; font-weight: 700; margin: 12mm 0 6mm; line-height: 1.15; page-break-after: avoid; }
h1.secao .numero { font-weight: 400; margin-right: 6pt; }
.sprint01:first-of-type h1.secao { margin-top: 0; }
h1.capitulo { font-size: 24pt; font-weight: 700; margin: 0 0 6mm; line-height: 1.15; page-break-before: always; }
h2 { font-size: 13.5pt; margin: 8mm 0 3mm; page-break-after: avoid; }
h3 { font-size: 12pt; margin: 6mm 0 2mm; page-break-after: avoid; }
p { margin: 0 0 3mm; text-align: justify; }
ul, ol { margin: 0 0 3mm; padding-left: 6mm; }
li { margin-bottom: 1mm; }
a { color: #000; }
code { font-family: Consolas, monospace; font-size: 9pt; background: #f2f2f2; padding: 0 2px; border-radius: 2px; }
blockquote { margin: 0 0 3mm; padding: 2mm 4mm; border-left: 3px solid #ababab; color: #333; }
table { width: 100%; border-collapse: collapse; margin: 2mm 0 5mm; font-size: 9pt; line-height: 1.35; page-break-inside: auto; }
tr { page-break-inside: avoid; }
th, td { border: 0.6pt solid #c8c8c8; padding: 3pt 5pt; text-align: left; vertical-align: top; }
th { background: #f2f2f2; font-weight: 700; }
figure { margin: 3mm 0 6mm; page-break-inside: avoid; }
figure img { width: 100%; border: 0.6pt solid #c8c8c8; }
figcaption { font-size: 9pt; color: #555; margin-top: 1.5mm; font-style: italic; }
p:has(> strong:only-child) + figure { margin-top: 0; }
.diagrama { margin: 3mm 0 6mm; text-align: center; page-break-inside: avoid; }
.diagrama svg { max-width: 100%; max-height: 200mm; height: auto; }
.diagrama-titulo { text-align: left; }
"""


def montar_html(partes, paginas):
    linhas_indice = []
    for i, (titulo, _, tipo) in enumerate(partes):
        classe = ' class="grupo"' if tipo != "sprint01" and (i == 0 or partes[i - 1][2] == "sprint01") else ""
        linhas_indice.append(f'<tr{classe}><td class="pagina">{paginas.get(titulo, 0):02d}</td><td>{html.escape(titulo)}</td></tr>')
    logo = (FERRAMENTAS / "logo-cabecalho.png").as_uri()
    corpo = "".join(f'<section class="{tipo}">{conteudo}</section>' for _, conteudo, tipo in partes)
    return f"""<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><title>Oráculo dos Direitos Trabalhistas - Sprints 01 a 09</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=PT+Sans:wght@400;700&family=PT+Serif:ital,wght@0,400;0,700;1,400&display=block" rel="stylesheet">
<style>{CSS}</style></head><body>
<section class="capa">
  <img class="logo" src="{logo}" alt="">
  <div class="curso">Ciência da Computação 8NA</div>
  <h1 class="titulo">Oráculo dos Direitos<br>Trabalhistas</h1>
  <div class="subtitulo">{SUBTITULO}</div>
  <table class="creditos"><tr><td>Apresentado para</td><td>Pryscilla de Barros Gonçalves</td></tr>
  <tr><td>Preparado pela equipe</td><td>Kaleido Void Studios</td></tr></table>
</section>
<section class="indice"><h1>Índice</h1><table>{''.join(linhas_indice)}</table></section>
{corpo}
<script src="https://cdn.jsdelivr.net/npm/mermaid@11.4.1/dist/mermaid.min.js"></script>
<script>
  mermaid.initialize({{ startOnLoad: false, theme: 'neutral', fontFamily: 'PT Serif, Georgia, serif', flowchart: {{ htmlLabels: true }} }});
  document.fonts.ready.then(() => mermaid.run()).then(() => {{ window.mermaidPronto = true; }});
</script>
</body></html>"""


def imprimir(html_texto, destino, pasta):
    arquivo = pasta / "relatorio.html"
    arquivo.write_text(html_texto, encoding="utf-8")
    with sync_playwright() as p:
        navegador = p.chromium.launch(channel="msedge")
        pagina = navegador.new_page()
        pagina.goto(arquivo.as_uri(), wait_until="networkidle")
        pagina.wait_for_function("window.mermaidPronto === true", timeout=60000)
        pagina.pdf(path=str(destino), format="A4", print_background=True, prefer_css_page_size=True)
        navegador.close()


def localizar_paginas(pdf, partes):
    """Página (numerada a partir da primeira seção) em que cada capítulo começa."""
    documento = fitz.open(pdf)
    textos = [documento[i].get_text() for i in range(documento.page_count)]
    primeira = next(i for i, t in enumerate(textos) if "Identificação da Equipe" in t and i > 0 and "Índice" not in t)
    paginas = {}
    for titulo, _, _ in partes:
        chave = titulo.split(" ", 1)[1] if titulo[0].isdigit() else titulo
        for i in range(primeira, len(textos)):
            if chave.replace("—", "").split()[0] in textos[i] and chave[:25] in " ".join(textos[i].split()):
                paginas[titulo] = i - primeira + 1
                break
    return paginas, primeira


def numerar(pdf, primeira):
    """Rodapé cinza à direita e número da página à esquerda, a partir da primeira seção (como no original)."""
    documento = fitz.open(pdf)
    cinza = (0.67, 0.67, 0.67)
    for i in range(1, documento.page_count):
        pagina = documento[i]
        largura, altura = pagina.rect.width, pagina.rect.height
        for linha, texto in enumerate(RODAPE):
            tamanho = fitz.get_text_length(texto, fontname="Times-Bold", fontsize=7.5)
            pagina.insert_text((largura - 57 - tamanho, altura - 46 + linha * 9.5), texto, fontname="Times-Bold", fontsize=7.5, color=cinza)
        if i >= primeira:
            pagina.insert_text((57, altura - 27), str(i - primeira + 1), fontname="Times-Roman", fontsize=9, color=cinza)
    documento.save(SAIDA, garbage=4, deflate=True)


def main():
    SAIDA.parent.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory() as temporaria:
        pasta = Path(temporaria)
        partes = capitulos(pasta)
        rascunho = pasta / "rascunho.pdf"
        imprimir(montar_html(partes, {}), rascunho, pasta)
        paginas, primeira = localizar_paginas(rascunho, partes)
        faltando = [t for t, _, _ in partes if t not in paginas]
        if faltando:
            print("Aviso: página não encontrada para", faltando, file=sys.stderr)
        final = pasta / "final.pdf"
        imprimir(montar_html(partes, paginas), final, pasta)
        numerar(final, primeira)
    print("Gerado:", SAIDA, f"({fitz.open(SAIDA).page_count} páginas)")


if __name__ == "__main__":
    main()
