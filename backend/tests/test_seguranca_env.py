"""Os arquivos .env.example vão para o GitHub (público): eles só podem ter nomes de variáveis.

As chaves reais ficam no backend/.env, que nunca é enviado. Este teste falha se
algum segredo for colocado no arquivo de exemplo por engano.
"""

from pathlib import Path

import pytest
from dotenv import dotenv_values

RAIZ = Path(__file__).resolve().parents[2]
EXEMPLOS = [RAIZ / "backend" / ".env.example"]

# Valores de exemplo que não são segredos
PERMITIDOS = {
    "SUPABASE_URL": "https://SEU-PROJETO.supabase.co",
}


@pytest.mark.parametrize("exemplo", EXEMPLOS, ids=lambda caminho: caminho.parent.name)
def test_env_example_nao_tem_segredos(exemplo):
    preenchidos = {
        nome: valor
        for nome, valor in dotenv_values(exemplo).items()
        if valor and PERMITIDOS.get(nome) != valor
    }
    assert not preenchidos, (
        f"O {exemplo.parent.name}/.env.example é público e não pode ter valores: {sorted(preenchidos)}. "
        "Coloque as chaves no .env, que não vai para o GitHub."
    )
