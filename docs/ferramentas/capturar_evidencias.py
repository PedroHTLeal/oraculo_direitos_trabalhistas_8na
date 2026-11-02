"""Percorre os fluxos do Oráculo no navegador e salva prints como evidência.

Usa o Microsoft Edge instalado no Windows (Playwright) e as contas de
demonstração do backend/.env (criadas por backend/scripts/criar_contas_demonstracao.py).

Com o sistema rodando em http://localhost:8000 (iniciar.bat):
    python docs/ferramentas/capturar_evidencias.py criar      # fluxos e cadastro de um trecho
    (encerre e abra o sistema de novo)
    python docs/ferramentas/capturar_evidencias.py conferir   # persistência e exclusões
"""

import json
import sys
import time
from pathlib import Path

from dotenv import dotenv_values
from playwright.sync_api import expect, sync_playwright

RAIZ = Path(__file__).resolve().parents[2]
PASTA = RAIZ / "docs" / "evidencias"
ESTADO = PASTA / "estado.json"
URL = "http://localhost:8000"
ENV = dotenv_values(RAIZ / "backend" / ".env")
CONTAS = {perfil: (ENV[f"DEMO_{perfil.upper()}_LOGIN"], ENV[f"DEMO_{perfil.upper()}_SENHA"]) for perfil in ("administrador", "curador", "usuario")}
TRECHO_DEMO = "Demonstração da Sprint 04"


class Roteiro:
    def __init__(self, pagina):
        self.pagina = pagina

    def print(self, nome, pagina_inteira=False):
        time.sleep(0.4)  # espera animações curtas
        self.pagina.screenshot(path=PASTA / f"{nome}.png", full_page=pagina_inteira)
        print("  print:", nome)

    def ir(self, caminho):
        self.pagina.goto(URL + caminho, wait_until="domcontentloaded")
        self.pagina.wait_for_load_state("networkidle")

    def entrar(self, perfil):
        login, senha = CONTAS[perfil]
        self.ir("/entrar")
        self.pagina.fill("#entrar-identificador", login)
        self.pagina.fill("#entrar-senha", senha)
        self.pagina.click("button[type=submit]")
        self.pagina.wait_for_url("**/painel/**")
        self.pagina.wait_for_load_state("networkidle")

    def sair(self):
        self.pagina.get_by_role("button", name="Sair").click()
        self.pagina.wait_for_url("**/entrar")


def criar(r):
    p = r.pagina

    print("Consulta pública")
    r.ir("/")
    r.print("01-consulta-inicial")

    print("Login: validações e erros")
    r.ir("/entrar")
    p.click("button[type=submit]")
    expect(p.get_by_text("Preencha o campo e-mail.")).to_be_visible()
    r.print("02-login-validacao")
    p.fill("#email", CONTAS["curador"][0])
    p.fill("#senha", "senha-errada-123")
    p.click("button[type=submit]")
    expect(p.get_by_text("E-mail ou senha incorretos.")).to_be_visible()
    r.print("03-login-senha-errada")

    print("Cadastro: validações, e-mail repetido e sucesso")
    r.ir("/cadastro")
    p.fill("#nome", "J")
    p.fill("#email", "joao@")
    p.fill("#senha", "123")
    p.fill("#confirmacao", "321")
    p.click("button[type=submit]")
    expect(p.get_by_text("Informe um e-mail válido, por exemplo nome@exemplo.com.")).to_be_visible()
    r.print("04-cadastro-validacao")
    p.fill("#nome", "João Teste")
    p.fill("#email", CONTAS["curador"][0])
    p.fill("#senha", "senha-teste-123")
    p.fill("#confirmacao", "senha-teste-123")
    p.click("button[type=submit]")
    expect(p.get_by_text("Já existe um usuário com este e-mail.")).to_be_visible()
    r.print("05-cadastro-email-repetido")
    email_novo = f"joao.teste{int(time.time())}@oraculo.com.br"
    p.fill("#email", email_novo)
    p.click("button[type=submit]")
    p.wait_for_url("**/painel/temas")
    expect(p.get_by_text("Conta criada!")).to_be_visible()
    r.print("06-cadastro-sucesso")
    r.sair()

    print("Perfil usuário: acompanhar tema e acesso negado")
    r.entrar("usuario")
    p.get_by_role("button", name="Acompanhar tema").click()
    expect(p.get_by_text("Preencha o campo tema.")).to_be_visible()
    r.print("07-temas-validacao")
    for inscricao in p.get_by_role("button", name="Deixar de acompanhar").all():
        inscricao.click()
        p.wait_for_load_state("networkidle")
    p.select_option("#tema", label="Férias")
    p.fill("#telefone", "11900000001")
    p.check("text=Autorizo o uso do meu telefone")
    p.get_by_role("button", name="Acompanhar tema").click()
    expect(p.get_by_text("Pronto! Você vai receber as novidades sobre Férias.")).to_be_visible()
    r.print("08-temas-inscricao")
    r.ir("/painel/base")
    expect(p.get_by_text("Acesso não permitido")).to_be_visible()
    r.print("09-usuario-sem-acesso")
    r.sair()

    print("Perfil curador: CRUD da base de conhecimento")
    r.entrar("curador")
    p.locator(".item-trecho").first.wait_for()
    r.print("10-base-lista")
    p.select_option("select", label="Contrato de Estágio")
    p.wait_for_load_state("networkidle")
    p.get_by_label("Buscar no texto").fill("recesso")
    p.get_by_role("button", name="Buscar").click()
    p.wait_for_load_state("networkidle")
    r.print("11-base-filtro")
    p.get_by_role("link", name="+ Novo trecho").click()
    p.get_by_role("button", name="Salvar").click()
    expect(p.get_by_text("Preencha o campo tema.")).to_be_visible()
    r.print("12-trecho-validacao")
    p.select_option("#tema", label="Férias")
    p.fill("#secao", TRECHO_DEMO)
    p.fill("#texto", "Trecho cadastrado pelo painel para demonstrar o CRUD da base de conhecimento.")
    p.get_by_role("button", name="Salvar").click()
    expect(p.get_by_text("Trecho cadastrado.")).to_be_visible()
    p.get_by_label("Buscar no texto").fill("Demonstração da Sprint")
    p.get_by_role("button", name="Buscar").click()
    p.wait_for_load_state("networkidle")
    r.print("13-trecho-cadastrado")
    p.get_by_role("link", name="Editar").first.click()
    p.wait_for_load_state("networkidle")
    p.fill("#texto", "Trecho cadastrado e depois editado pelo painel, para demonstrar o CRUD da base de conhecimento.")
    r.print("14-trecho-edicao")
    p.get_by_role("button", name="Salvar").click()
    expect(p.get_by_text("Trecho atualizado.")).to_be_visible()
    r.print("15-trecho-atualizado")
    r.ir("/painel/usuarios")
    expect(p.get_by_text("Acesso não permitido")).to_be_visible()
    r.print("16-curador-sem-acesso")
    r.sair()

    ESTADO.write_text(json.dumps({"email_cadastrado": email_novo}), encoding="utf-8")
    print("\nEncerre e abra o sistema de novo e rode: capturar_evidencias.py conferir")


def conferir(r):
    p = r.pagina
    estado = json.loads(ESTADO.read_text(encoding="utf-8"))

    print("Persistência: o trecho continua salvo após reiniciar")
    r.entrar("curador")
    r.ir("/painel/base?busca=Demonstra%C3%A7%C3%A3o%20da%20Sprint")
    expect(p.get_by_role("heading", name=TRECHO_DEMO)).to_be_visible()
    r.print("17-persistencia-apos-reiniciar")
    p.get_by_role("button", name="Excluir").first.click()
    r.print("18-trecho-confirmar-exclusao")
    p.get_by_role("dialog").get_by_role("button", name="Excluir").click()
    expect(p.get_by_text("Trecho excluído.")).to_be_visible()
    r.print("19-trecho-excluido")
    r.sair()

    print("Perfil administrador: usuários")
    r.entrar("administrador")
    r.ir("/painel/usuarios")
    r.print("20-usuarios-lista")
    p.get_by_role("button", name="+ Novo usuário").click()
    p.get_by_role("dialog").get_by_role("button", name="Salvar").click()
    expect(p.get_by_text("Preencha o campo nome.")).to_be_visible()
    r.print("21-usuario-validacao")
    p.get_by_role("button", name="Fechar").click()

    linha_admin = p.get_by_role("row").filter(has_text=CONTAS["administrador"][0])
    linha_admin.get_by_role("button", name="Editar").click()
    p.select_option("#usuario-perfil", "curador")
    p.get_by_role("dialog").get_by_role("button", name="Salvar").click()
    expect(p.get_by_role("dialog").get_by_role("alert")).to_be_visible()
    r.print("22-regra-administrador")
    p.get_by_role("button", name="Fechar").click()

    linha = p.get_by_role("row").filter(has_text=estado["email_cadastrado"])
    linha.get_by_role("button", name="Excluir").click()
    r.print("23-usuario-confirmar-exclusao")
    p.get_by_role("dialog").get_by_role("button", name="Excluir").click()
    expect(p.get_by_text("Usuário excluído.")).to_be_visible()
    r.print("24-usuario-excluido")
    r.ir("/painel/perguntas")
    r.print("25-perguntas-recebidas")
    r.sair()

    print("Celular")
    p.set_viewport_size({"width": 390, "height": 844})
    r.ir("/")
    r.print("26-celular-consulta")
    r.entrar("curador")
    r.print("27-celular-painel")


def main():
    fase = sys.argv[1] if len(sys.argv) > 1 else "criar"
    PASTA.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        navegador = playwright.chromium.launch(channel="msedge")
        pagina = navegador.new_page(viewport={"width": 1366, "height": 800}, device_scale_factor=1.5, locale="pt-BR")
        pagina.set_default_timeout(15000)
        {"criar": criar, "conferir": conferir}[fase](Roteiro(pagina))
        navegador.close()


if __name__ == "__main__":
    main()
