"""O backend/.env.example vai para o GitHub (público): ele só pode ter nomes de variáveis.

As chaves reais ficam no backend/.env, que nunca é enviado. Este teste falha se
algum segredo for colocado no arquivo de exemplo por engano.
"""

from pathlib import Path

from dotenv import dotenv_values

EXEMPLO = Path(__file__).resolve().parent.parent / ".env.example"

# Valores de exemplo que não são segredos
PERMITIDOS = {
    "SUPABASE_URL": "https://SEU-PROJETO.supabase.co",
    "PROVEDOR_WHATSAPP": "meta",
    "TWILIO_WHATSAPP_NUMERO": "+14155238886",
}


def test_env_example_nao_tem_segredos():
    preenchidos = {
        nome: valor
        for nome, valor in dotenv_values(EXEMPLO).items()
        if valor and PERMITIDOS.get(nome) != valor
    }
    assert not preenchidos, (
        f"O backend/.env.example é público e não pode ter valores: {sorted(preenchidos)}. "
        "Coloque as chaves no backend/.env."
    )
