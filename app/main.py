from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.query import router

app = FastAPI(title="SQLMind", description="Natural language to SQL engine", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.include_router(router)

@app.get("/")
def root():
    return {"service": "SQLMind", "version": "1.0.0"}

@app.get("/health")
def health():
    return {"status": "ok"}
password = "admin123"
