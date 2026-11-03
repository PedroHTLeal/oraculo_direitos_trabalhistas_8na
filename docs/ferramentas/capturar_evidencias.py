"""Percorre os fluxos do Oráculo no navegador e salva prints como evidência.

Usa o Microsoft Edge instalado no Windows (Playwright) e as contas de
demonstração do backend/.env (criadas por backend/scripts/criar_contas_demonstracao.py).
Cada verificação (expect) que falha interrompe o roteiro: ele também é um teste
de navegação.

Com o sistema rodando em http://localhost:8000 (iniciar.bat):
    python docs/ferramentas/capturar_evidencias.py criar      # fluxos e cadastros
    (encerre e abra o sistema de novo)
    python docs/ferramentas/capturar_evidencias.py conferir   # persistência, relatórios e exclusões
"""

import json
import random
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
CONTAS = {
    perfil: (ENV[f"DEMO_{perfil.upper()}_LOGIN"], ENV[f"DEMO_{perfil.upper()}_SENHA"])
    for perfil in ("administrador", "curador", "usuario")
}
TRECHO_DEMO = "Demonstração das Sprints"
ATUALIZACAO_DEMO = "Novidade de demonstração sobre férias"


class Roteiro:
    def __init__(self, pagina):
        self.pagina = pagina

    def print(self, nome, pagina_inteira=False):
        time.sleep(0.5)  # espera animações curtas
        self.pagina.screenshot(path=PASTA / f"{nome}.png", full_page=pagina_inteira)
        print("  print:", nome)

    def ir(self, caminho):
        self.pagina.goto(URL + caminho, wait_until="domcontentloaded")
        self.pagina.wait_for_load_state("networkidle")

    def entrar(self, perfil):
        login, senha = CONTAS[perfil]
        self.ir("/entrar")
        self.pagina.fill("#entrar-email", login)
        self.pagina.fill("#entrar-senha", senha)
        self.pagina.get_by_role("button", name="Entrar", exact=True).last.click()
        self.pagina.wait_for_url("**/painel/**")
        self.pagina.wait_for_load_state("networkidle")

    def sair(self):
        self.pagina.get_by_role("button", name="Sair").click()
        self.pagina.wait_for_url("**/entrar")

    def baixar(self, nome_botao, arquivo):
        with self.pagina.expect_download() as download:
            self.pagina.get_by_role("button", name=nome_botao).click()
        download.value.save_as(PASTA / arquivo)
        print("  arquivo:", arquivo)


def criar(r):
    p = r.pagina

    print("Consulta pública")
    r.ir("/")
    r.print("01-consulta-inicial")

    print("Login: validações e erros")
    r.ir("/entrar")
    p.get_by_role("button", name="Entrar", exact=True).last.click()
    expect(p.get_by_text("Preencha o campo e-mail.")).to_be_visible()
    r.print("02-login-validacao")
    p.fill("#entrar-email", "ninguem@example.com")
    p.fill("#entrar-senha", "senha-errada-123")
    p.get_by_role("button", name="Entrar", exact=True).last.click()
    expect(p.get_by_text("E-mail ou senha incorretos.")).to_be_visible()
    r.print("03-login-senha-errada")

    print("Cadastro: validações, e-mail repetido e sucesso")
    r.ir("/cadastro")
    p.fill("#cadastro-nome", "J")
    p.fill("#cadastro-email", "joao")
    p.fill("#cadastro-senha", "123")
    p.fill("#cadastro-confirmacao", "321")
    p.get_by_role("button", name="Criar conta").click()
    expect(p.get_by_text("Informe um e-mail válido, por exemplo nome@exemplo.com.")).to_be_visible()
    r.print("04-cadastro-validacao")
    p.fill("#cadastro-nome", "João Teste")
    p.fill("#cadastro-email", CONTAS["usuario"][0])
    p.fill("#cadastro-senha", "senha-teste-123")
    p.fill("#cadastro-confirmacao", "senha-teste-123")
    p.check("text=Autorizo o uso do meu e-mail")
    p.get_by_role("button", name="Criar conta").click()
    expect(p.get_by_text("Já existe um usuário com este e-mail.", exact=False)).to_be_visible()
    r.print("05-cadastro-email-repetido")
    email_novo = f"joao.teste{random.randint(1000, 9999)}@example.com"
    p.fill("#cadastro-email", email_novo)
    p.get_by_role("button", name="Criar conta").click()
    p.wait_for_url("**/painel/temas")
    expect(p.get_by_text("Conta criada!")).to_be_visible()
    r.print("06-cadastro-sucesso")
    r.sair()

    print("Perfil usuário: acompanhar tema e acesso negado")
    r.entrar("usuario")
    # Começa sem temas acompanhados (remove os de execuções anteriores)
    p.locator(".lista-inscricoes").or_(p.get_by_text("Você ainda não acompanha nenhum tema.")).first.wait_for()
    deixar = p.get_by_role("button", name="Deixar de acompanhar")
    while deixar.count():
        quantidade = deixar.count()
        deixar.first.click()
        expect(deixar).to_have_count(quantidade - 1)
    p.get_by_role("button", name="Acompanhar tema").click()
    expect(p.get_by_text("Preencha o campo tema.")).to_be_visible()
    r.print("07-temas-validacao")
    p.select_option("#tema", label="Férias")
    p.get_by_role("button", name="Acompanhar tema").click()
    expect(p.get_by_text("Pronto! Você vai receber as novidades sobre Férias.")).to_be_visible()
    r.print("08-temas-inscricao")
    r.ir("/painel/base")
    expect(p.get_by_text("Acesso não permitido")).to_be_visible()
    r.print("09-usuario-sem-acesso")
    r.sair()

    print("Perfil curador: dashboard e CRUD da base de conhecimento")
    r.entrar("curador")
    p.locator(".indicador").first.wait_for()
    r.print("10-dashboard", pagina_inteira=True)
    r.ir("/painel/base")
    p.locator(".item-trecho").first.wait_for()
    r.print("11-base-lista")
    p.select_option("select", label="Contrato de Estágio")
    p.wait_for_load_state("networkidle")
    p.get_by_label("Buscar no texto").fill("recesso")
    p.get_by_role("button", name="Buscar").click()
    p.wait_for_load_state("networkidle")
    p.locator(".item-trecho").first.wait_for()
    r.print("12-base-filtro")
    p.get_by_role("link", name="+ Novo trecho").click()
    p.get_by_role("button", name="Salvar").click()
    expect(p.get_by_text("Preencha o campo tema.")).to_be_visible()
    r.print("13-trecho-validacao")
    p.select_option("#tema", label="Férias")
    p.fill("#secao", TRECHO_DEMO)
    p.fill("#texto", "Trecho cadastrado pelo painel para demonstrar o CRUD da base de conhecimento.")
    p.get_by_role("button", name="Salvar").click()
    expect(p.get_by_text("Trecho cadastrado.")).to_be_visible()
    p.get_by_label("Buscar no texto").fill(TRECHO_DEMO)
    p.get_by_role("button", name="Buscar").click()
    expect(p.get_by_role("heading", name=TRECHO_DEMO)).to_be_visible()
    r.print("14-trecho-cadastrado")
    p.get_by_role("link", name="Editar").first.click()
    p.wait_for_load_state("networkidle")
    p.fill("#texto", "Trecho cadastrado e depois editado pelo painel, para demonstrar o CRUD da base de conhecimento.")
    r.print("15-trecho-edicao")
    p.get_by_role("button", name="Salvar").click()
    expect(p.get_by_text("Trecho atualizado.")).to_be_visible()
    r.print("16-trecho-atualizado")

    print("Módulo 2: publicar atualização")
    r.ir("/painel/atualizacoes")
    p.get_by_role("button", name="Publicar e enviar").click()
    expect(p.get_by_text("Preencha o campo título.")).to_be_visible()
    r.print("17-atualizacao-validacao")
    p.select_option("#atualizacao-tema", label="Férias")
    p.fill("#atualizacao-titulo", ATUALIZACAO_DEMO)
    p.fill("#atualizacao-conteudo", "A cartilha explica que as férias devem ser pagas até 2 dias antes do início do descanso.")
    p.fill("#atualizacao-url", "https://www.trt4.jus.br/portais/trt4/ferias")
    p.get_by_role("button", name="Publicar e enviar").click()
    expect(p.get_by_text("Atualização publicada.")).to_be_visible()
    time.sleep(3)
    r.ir("/painel/atualizacoes")
    expect(p.get_by_role("heading", name=ATUALIZACAO_DEMO).first).to_be_visible()
    r.print("18-atualizacao-publicada", pagina_inteira=True)
    r.ir("/painel/historico")
    expect(p.get_by_text("Acesso não permitido")).to_be_visible()
    r.print("19-curador-sem-acesso-historico")
    r.sair()

    ESTADO.write_text(json.dumps({"email_cadastrado": email_novo}), encoding="utf-8")
    print("\nEncerre e abra o sistema de novo e rode: capturar_evidencias.py conferir")


def conferir(r):
    p = r.pagina
    estado = json.loads(ESTADO.read_text(encoding="utf-8"))

    print("Persistência: o trecho continua salvo depois de reiniciar o sistema")
    r.entrar("curador")
    r.ir("/painel/base?busca=" + TRECHO_DEMO.replace(" ", "%20"))
    expect(p.get_by_role("heading", name=TRECHO_DEMO)).to_be_visible()
    r.print("20-persistencia-apos-reiniciar")
    p.get_by_role("button", name="Excluir").first.click()
    r.print("21-trecho-confirmar-exclusao")
    p.get_by_role("dialog").get_by_role("button", name="Excluir").click()
    expect(p.get_by_text("Trecho excluído.")).to_be_visible()
    r.print("22-trecho-excluido")

    print("Relatório de perguntas e exportação")
    r.ir("/painel/relatorios")
    p.wait_for_load_state("networkidle")
    r.print("23-relatorio-perguntas")
    r.baixar("Exportar CSV", "relatorio-perguntas.csv")
    r.sair()

    print("Perfil usuário: novidade do tema acompanhado")
    r.entrar("usuario")
    expect(p.get_by_role("heading", name=ATUALIZACAO_DEMO).first).to_be_visible()
    r.print("24-usuario-novidades", pagina_inteira=True)
    r.sair()

    print("Perfil administrador: usuários, regras e histórico")
    r.entrar("administrador")
    r.ir("/painel/usuarios")
    r.print("25-usuarios-lista")
    p.get_by_role("button", name="+ Novo usuário").click()
    p.get_by_role("dialog").get_by_role("button", name="Salvar").click()
    expect(p.get_by_text("Preencha o campo nome.")).to_be_visible()
    r.print("26-usuario-validacao")
    p.get_by_role("button", name="Fechar").click()

    linha_admin = p.get_by_role("row").filter(has_text=CONTAS["administrador"][0])
    linha_admin.get_by_role("button", name="Editar").click()
    p.select_option("#usuario-perfil", "curador")
    p.get_by_role("dialog").get_by_role("button", name="Salvar").click()
    expect(p.get_by_role("dialog").get_by_role("alert")).to_be_visible()
    r.print("27-regra-administrador")
    p.get_by_role("button", name="Fechar").click()

    linha = p.get_by_role("row").filter(has_text=estado["email_cadastrado"])
    linha.get_by_role("button", name="Excluir").click()
    r.print("28-usuario-confirmar-exclusao")
    p.get_by_role("dialog").get_by_role("button", name="Excluir").click()
    expect(p.get_by_text("Usuário excluído.")).to_be_visible()
    r.print("29-usuario-excluido")

    r.ir("/painel/historico")
    p.wait_for_load_state("networkidle")
    r.print("30-historico")
    p.locator("label.filtro").filter(has_text="Ação").locator("select").select_option(label="Exclusão")
    p.get_by_role("button", name="Filtrar").click()
    p.wait_for_load_state("networkidle")
    r.print("31-historico-filtro-exclusao")
    r.baixar("Exportar CSV", "historico-de-operacoes.csv")
    r.ir("/painel/dashboard")
    p.locator(".indicador").first.wait_for()
    r.print("32-dashboard-administrador", pagina_inteira=True)
    r.sair()

    print("Celular")
    p.set_viewport_size({"width": 390, "height": 844})
    r.ir("/")
    r.print("33-celular-consulta")
    r.ir("/cadastro")
    r.print("34-celular-cadastro")
    r.entrar("curador")
    r.print("35-celular-painel")


def main():
    fase = sys.argv[1] if len(sys.argv) > 1 else "criar"
    PASTA.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        navegador = playwright.chromium.launch(channel="msedge")
        pagina = navegador.new_page(
            viewport={"width": 1366, "height": 800}, device_scale_factor=1.5, locale="pt-BR", accept_downloads=True
        )
        pagina.set_default_timeout(15000)
        {"criar": criar, "conferir": conferir}[fase](Roteiro(pagina))
        navegador.close()


if __name__ == "__main__":
    main()
