from fastapi import FastAPI

app = FastAPI(title="Oráculo dos Direitos Trabalhistas")


@app.get("/api/saude")
def saude():
    return {"status": "ok"}
