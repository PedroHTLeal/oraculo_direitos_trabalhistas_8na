import re


class TelefoneInvalido(ValueError):
    pass


def normalizar_telefone(texto):
    """Converte um telefone brasileiro para o formato internacional (+55DDDNUMERO).

    Aceita formatos como "(51) 99999-8888", "51999998888" ou "+55 51 99999-8888".
    """
    digitos = re.sub(r"\D", "", texto or "")
    if digitos.startswith("55") and len(digitos) in (12, 13):
        digitos = digitos[2:]
    if len(digitos) not in (10, 11):
        raise TelefoneInvalido("Informe o telefone com DDD, por exemplo (51) 99999-8888.")
    ddd = int(digitos[:2])
    if ddd < 11 or ddd > 99 or digitos[2] == "0":
        raise TelefoneInvalido("O DDD ou o número informado não é válido.")
    return f"+55{digitos}"
