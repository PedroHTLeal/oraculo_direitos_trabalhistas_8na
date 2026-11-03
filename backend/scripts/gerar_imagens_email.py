"""Gera as imagens PNG usadas nos e-mails (o Gmail não exibe SVG).

Desenha o símbolo do Oráculo e a balança da tela inicial com as cores da
identidade visual. Rode de novo só se o desenho mudar (precisa do Pillow,
em requirements-dev.txt).

Uso (na pasta backend/):
    python scripts/gerar_imagens_email.py
"""

from pathlib import Path

from PIL import Image, ImageDraw

PASTA = Path(__file__).resolve().parent.parent / "app" / "recursos"
MARINHO = (3, 12, 44, 255)
DOURADO = (232, 178, 15, 255)
BRANCO = (255, 255, 255, 255)
ESCALA = 16  # desenha grande e reduz, para as bordas ficarem suaves


def circulo(desenho, cx, cy, raio, cor):
    s = ESCALA
    desenho.ellipse([(cx - raio) * s, (cy - raio) * s, (cx + raio) * s, (cy + raio) * s], fill=cor)


def linha(desenho, inicio, fim, largura, cor):
    s = ESCALA
    desenho.line([inicio[0] * s, inicio[1] * s, fim[0] * s, fim[1] * s], fill=cor, width=round(largura * s))
    # Pontas arredondadas, como no SVG do site
    for x, y in (inicio, fim):
        circulo(desenho, x, y, largura / 2, cor)


def salvar(imagem, tamanho, nome):
    imagem.resize((tamanho, tamanho), Image.LANCZOS).save(PASTA / nome)
    print("gerado:", PASTA / nome)


def simbolo():
    """Anel branco com o ponto dourado (logo do cabeçalho), viewBox 40x40."""
    imagem = Image.new("RGBA", (40 * ESCALA, 40 * ESCALA), (0, 0, 0, 0))
    desenho = ImageDraw.Draw(imagem)
    s = ESCALA
    desenho.ellipse([2.5 * s, 2.5 * s, 37.5 * s, 37.5 * s], outline=BRANCO, width=5 * s)
    circulo(desenho, 31, 9, 6.75, MARINHO)
    circulo(desenho, 31, 9, 4.25, DOURADO)
    salvar(imagem, 96, "email-simbolo.png")


def medalha():
    """Círculo dourado com a balança da justiça, viewBox 64x64."""
    imagem = Image.new("RGBA", (64 * ESCALA, 64 * ESCALA), (0, 0, 0, 0))
    desenho = ImageDraw.Draw(imagem)
    circulo(desenho, 32, 32, 31, DOURADO)
    largura, d = 2.6, 8  # traço e deslocamento da balança dentro do círculo

    def p(x, y):
        return (x + d, y + d)

    for inicio, fim in (
        ((24, 9), (24, 38)),
        ((15, 38), (33, 38)),
        ((11, 15), (37, 15)),
        ((11, 15), (5, 27)),
        ((11, 15), (17, 27)),
        ((37, 15), (31, 27)),
        ((37, 15), (43, 27)),
    ):
        linha(desenho, p(*inicio), p(*fim), largura, MARINHO)
    s = ESCALA
    for cx in (11, 37):  # pratos da balança: meia-volta para baixo
        x, y = p(cx, 27)
        desenho.arc([(x - 6) * s, (y - 6) * s, (x + 6) * s, (y + 6) * s], 0, 180, fill=MARINHO, width=round(largura * s))
    salvar(imagem, 128, "email-balanca.png")


if __name__ == "__main__":
    PASTA.mkdir(exist_ok=True)
    simbolo()
    medalha()
