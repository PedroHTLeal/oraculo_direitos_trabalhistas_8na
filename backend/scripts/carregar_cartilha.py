"""Envia a cartilha de dados/cartilha.json para as tabelas "temas" e "trechos" do Supabase.

Pode ser executado de novo sempre que a cartilha for extraída outra vez:
temas e trechos existentes são atualizados e os que deixaram de existir são removidos.

Uso (na pasta backend/, com o .env preenchido):
    python scripts/carregar_cartilha.py
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import carregar_configuracao  # noqa: E402
from supabase import create_client  # noqa: E402

ARQUIVO = Path(__file__).resolve().parent.parent / "dados" / "cartilha.json"


def main():
    config = carregar_configuracao()
    cliente = create_client(config.supabase_url, config.supabase_chave_servico)
    trechos = json.loads(ARQUIVO.read_text(encoding="utf-8"))

    # Temas: um por página da cartilha; o slug é o final do endereço
    temas = {}
    for trecho in trechos:
        temas.setdefault(trecho["tema"], {"nome": trecho["tema"], "url": trecho["url"], "slug": trecho["url"].rstrip("/").rsplit("/", 1)[-1]})
    salvos = cliente.table("temas").upsert(list(temas.values()), on_conflict="nome").execute().data
    id_do_tema = {tema["nome"]: tema["id"] for tema in salvos}

    registros = [
        {"tema_id": id_do_tema[t["tema"]], "secao": t["secao"], "ordem": t["ordem"], "texto": t["texto"]}
        for t in trechos
    ]
    cliente.table("trechos").upsert(registros, on_conflict="tema_id,ordem").execute()

    # Remove trechos e temas que não existem mais na cartilha
    atuais = {(r["tema_id"], r["ordem"]) for r in registros}
    no_banco = cliente.table("trechos").select("id,tema_id,ordem").execute().data
    obsoletos = [t["id"] for t in no_banco if (t["tema_id"], t["ordem"]) not in atuais]
    if obsoletos:
        cliente.table("trechos").delete().in_("id", obsoletos).execute()
    temas_obsoletos = [t["id"] for t in cliente.table("temas").select("id,nome").execute().data if t["nome"] not in temas]
    if temas_obsoletos:
        cliente.table("temas").delete().in_("id", temas_obsoletos).execute()

    print(f"{len(temas)} temas e {len(registros)} trechos carregados; {len(obsoletos)} trechos removidos.")


if __name__ == "__main__":
    main()
