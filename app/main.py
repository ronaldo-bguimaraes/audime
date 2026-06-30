from fastapi import FastAPI

from app.api.v1.endpoints import analytics, auth, extracoes, faturas, notas

app = FastAPI(title="Audime API", version="1.0.0")

app.include_router(auth.router)
app.include_router(extracoes.router)
app.include_router(notas.router)
app.include_router(faturas.router)
app.include_router(analytics.router)


@app.get("/v1/health")
def health():
    return {"status": "ok"}
