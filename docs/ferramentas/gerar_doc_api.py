"""Gera docs/api.md a partir da especificação OpenAPI do backend (a mesma do Swagger em /api/docs).

Uso (na raiz do projeto):
    backend\\.venv\\Scripts\\python docs\\ferramentas\\gerar_doc_api.py
"""

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "backend"))

from app.documentacao_api import ROTAS, TEMAS  # noqa: E402
from app.main import app  # noqa: E402

SAIDA = RAIZ / "docs" / "api.md"
SITE = "https://oraculo-direitos-trabalhistas-8na.vercel.app"
NOMES_STATUS = {
    "200": "OK", "201": "Criado", "202": "Aceito (envio em andamento)", "204": "Sem conteúdo",
    "401": "Sem login ou sessão expirada", "403": "Perfil sem permissão", "404": "Não encontrado",
    "409": "Registro repetido", "422": "Dados inválidos", "429": "Muitos pedidos", "502": "IA indisponível",
    "503": "Serviço não configurado",
}

EXEMPLOS = f"""## Exemplos de uso

Fazer uma pergunta (aberta, sem login):

```bash
curl -X POST {SITE}/api/perguntas \\
  -H "Content-Type: application/json" \\
  -d '{{"texto": "Quantos dias de férias eu tenho direito?"}}'
```

```json
{{
  "id": "5f0c…",
  "pergunta": "Quantos dias de férias eu tenho direito?",
  "resposta": "Você tem direito a 30 dias de férias por ano…",
  "encontrou": true,
  "fontes": [{{"titulo": "Férias · Pagamento das férias", "trecho": "…", "url": "https://www.trt4.jus.br/portais/trt4/ferias"}}]
}}
```

Pedir mais conteúdo por e-mail:

```bash
curl -X POST {SITE}/api/saiba-mais \\
  -H "Content-Type: application/json" \\
  -d '{{"pergunta_id": "5f0c…", "nome": "Maria", "email": "maria@exemplo.com", "consentimento": true}}'
```

Entrar e usar o token em uma rota da equipe:

```bash
curl -X POST {SITE}/api/auth/login \\
  -H "Content-Type: application/json" \\
  -d '{{"email": "curador@exemplo.com", "senha": "sua-senha"}}'
# resposta: {{"token": "…", "usuario": {{…}}}}

curl {SITE}/api/base/trechos?tema_id=7 -H "Authorization: Bearer <token>"
```

Erro de validação (422):

```json
{{"detail": "Preencha o campo e-mail.", "erros": ["Preencha o campo e-mail."]}}
```
"""


def resolver(esquema, especificacao):
    if "$ref" in esquema:
        nome = esquema["$ref"].split("/")[-1]
        return nome, especificacao["components"]["schemas"][nome]
    return None, esquema


def tipo(esquema, especificacao):
    if "$ref" in esquema:
        return f"`{esquema['$ref'].split('/')[-1]}`"
    if "anyOf" in esquema:
        partes = [tipo(s, especificacao) for s in esquema["anyOf"] if s.get("type") != "null"]
        return " ou ".join(partes) + " (opcional)" if len(partes) < len(esquema["anyOf"]) else " ou ".join(partes)
    if esquema.get("type") == "array":
        return f"lista de {tipo(esquema.get('items', {}), especificacao)}"
    if "enum" in esquema:
        return " / ".join(f"`{v}`" for v in esquema["enum"])
    nomes = {"string": "texto", "integer": "número inteiro", "boolean": "verdadeiro/falso", "number": "número", "object": "objeto"}
    base = nomes.get(esquema.get("type"), esquema.get("type", "qualquer"))
    return "e-mail" if esquema.get("format") == "email" else base


def regras(esquema):
    alvo = next((s for s in esquema.get("anyOf", []) if s.get("type") != "null"), esquema)
    itens = []
    if "minLength" in alvo:
        itens.append(f"mín. {alvo['minLength']} caracteres")
    if "maxLength" in alvo:
        itens.append(f"máx. {alvo['maxLength']} caracteres")
    if "minimum" in alvo:
        itens.append(f"mín. {alvo['minimum']}")
    if "maximum" in alvo:
        itens.append(f"máx. {alvo['maximum']}")
    if "pattern" in alvo:
        itens.append("começa com http:// ou https://" if "https?" in alvo["pattern"] else f"formato `{alvo['pattern']}`")
    if "default" in alvo or "default" in esquema:
        itens.append(f"padrão: `{esquema.get('default', alvo.get('default'))}`")
    return "; ".join(itens) or "—"


def tabela_campos(esquema, especificacao):
    obrigatorios = set(esquema.get("required", []))
    linhas = ["| Campo | Tipo | Obrigatório | Regras |", "| --- | --- | --- | --- |"]
    for nome, campo in esquema.get("properties", {}).items():
        linhas.append(f"| `{nome}` | {tipo(campo, especificacao)} | {'Sim' if nome in obrigatorios else 'Não'} | {regras(campo)} |")
    return linhas


def rota_md(metodo, caminho, operacao, especificacao):
    resumo, descricao, acesso = ROTAS[(metodo.upper(), caminho)]
    linhas = [f"### {resumo}", "", f"`{metodo.upper()} {caminho}` · **Acesso:** {acesso}", "", descricao, ""]
    parametros = operacao.get("parameters", [])
    if parametros:
        linhas += ["**Parâmetros**", "", "| Nome | Onde | Tipo | Obrigatório | Regras |", "| --- | --- | --- | --- | --- |"]
        for p in parametros:
            onde = {"path": "rota", "query": "consulta (?)"}.get(p["in"], p["in"])
            linhas.append(f"| `{p['name']}` | {onde} | {tipo(p['schema'], especificacao)} | {'Sim' if p.get('required') else 'Não'} | {regras(p['schema'])} |")
        linhas.append("")
    corpo = operacao.get("requestBody", {}).get("content", {}).get("application/json", {}).get("schema")
    if corpo:
        nome, esquema = resolver(corpo, especificacao)
        linhas += [f"**Corpo (JSON{', ' + nome if nome else ''})**", "", *tabela_campos(esquema, especificacao), ""]
    respostas = []
    for status, resposta in operacao.get("responses", {}).items():
        if status == "422":
            continue
        conteudo = resposta.get("content", {}).get("application/json", {}).get("schema")
        respostas.append(f"`{status}` {NOMES_STATUS.get(status, '')}" + (f": {tipo(conteudo, especificacao)}" if conteudo and conteudo != {} else ""))
    linhas += ["**Respostas:** " + " · ".join(respostas), ""]
    return linhas


def main():
    especificacao = app.openapi()
    linhas = [
        "# Documentação da API",
        "",
        f"**Versão:** {especificacao['info']['version']} (Release Candidate) · **Base:** `{SITE}` · "
        f"**Documentação interativa (Swagger):** [{SITE}/api/docs]({SITE}/api/docs)",
        "",
        "Gerada a partir da especificação OpenAPI do backend por [`docs/ferramentas/gerar_doc_api.py`](ferramentas/gerar_doc_api.py). "
        "No Swagger é possível testar cada rota pelo navegador (botão *Authorize* para usar o token).",
        "",
        especificacao["info"]["description"],
        "",
        "## Resumo das rotas",
        "",
        "| Método | Rota | O que faz | Acesso |",
        "| --- | --- | --- | --- |",
    ]
    por_tema = {t["name"]: [] for t in TEMAS}
    por_tema["Outros"] = []
    for caminho, metodos in especificacao["paths"].items():
        for metodo, operacao in metodos.items():
            resumo, _, acesso = ROTAS[(metodo.upper(), caminho)]
            linhas.append(f"| `{metodo.upper()}` | `{caminho}` | {resumo} | {acesso} |")
            tema = (operacao.get("tags") or ["Outros"])[0]
            por_tema.setdefault(tema, []).append((metodo, caminho, operacao))
    linhas.append("")
    for tema in TEMAS + [{"name": "Outros", "description": "Situação do serviço."}]:
        rotas = por_tema.get(tema["name"])
        if not rotas:
            continue
        linhas += [f"## {tema['name']}", "", tema["description"], ""]
        for metodo, caminho, operacao in rotas:
            linhas += rota_md(metodo, caminho, operacao, especificacao)
    linhas.append(EXEMPLOS)
    SAIDA.write_text("\n".join(linhas), encoding="utf-8")
    print("Gerado:", SAIDA, f"({sum(len(m) for m in especificacao['paths'].values())} rotas)")


if __name__ == "__main__":
    main()
