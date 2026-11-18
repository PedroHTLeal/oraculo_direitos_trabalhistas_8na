from app.documentacao_api import ROTAS
from app.main import app


def rotas_da_api():
    return {
        (metodo, rota.path)
        for rota in app.routes
        if rota.path.startswith("/api/") and getattr(rota, "include_in_schema", True) and rota.path not in ("/api/docs", "/api/openapi.json")
        for metodo in getattr(rota, "methods", None) or ()
        if metodo not in ("HEAD", "OPTIONS")
    }


def test_toda_rota_esta_documentada():
    # Uma rota nova sem resumo e acesso em documentacao_api.py faz este teste falhar
    assert rotas_da_api() - set(ROTAS) == set()
    assert set(ROTAS) - rotas_da_api() == set()


def test_swagger_e_openapi_ficam_sob_api(client):
    assert client.get("/api/docs").status_code == 200
    especificacao = client.get("/api/openapi.json").json()
    assert especificacao["info"]["version"] == "1.0.0-rc.5"
    assert especificacao["paths"]["/api/perguntas"]["post"]["summary"] == "Fazer uma pergunta"
    assert "Acesso:** Aberta" in especificacao["paths"]["/api/perguntas"]["post"]["description"]
