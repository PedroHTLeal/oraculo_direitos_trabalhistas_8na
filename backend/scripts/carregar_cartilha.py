"""Envia os trechos de dados/cartilha.json para a tabela "trechos" do Supabase.

Pode ser executado de novo sempre que a cartilha for extraída outra vez:
trechos existentes são atualizados e os que deixaram de existir são removidos.

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

    cliente.table("trechos").upsert(trechos, on_conflict="url,ordem").execute()

    # Remove trechos que não existem mais na cartilha
    atuais = {(t["url"], t["ordem"]) for t in trechos}
    no_banco = cliente.table("trechos").select("id,url,ordem").execute().data
    obsoletos = [t["id"] for t in no_banco if (t["url"], t["ordem"]) not in atuais]
    if obsoletos:
        cliente.table("trechos").delete().in_("id", obsoletos).execute()

    print(f"{len(trechos)} trechos carregados; {len(obsoletos)} removidos.")


if __name__ == "__main__":
    main()
