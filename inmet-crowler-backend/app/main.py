from fastapi import FastAPI
from routes.health import router as health_router
from routes.excel import router as excel_router

app = FastAPI()
app.include_router(health_router)
app.include_router(excel_router)

@app.get("/")
def read_root():
    return {"message": "API rodando com sucesso 🚀"}


