import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import init_db
from app.routes import contracts
from app.routes import dashboard

app = FastAPI(
    title="RiskLens AI",
    version="1.0.0"
)

# Comma-separated list of allowed frontend origins, e.g.
# ALLOWED_ORIGINS=https://risklens.vercel.app,http://localhost:3000
# Defaults to "*" (open) if unset - set it in production.
_origins_env = os.getenv("ALLOWED_ORIGINS", "").strip()
origins = [o.strip().rstrip("/") for o in _origins_env.split(",") if o.strip()] or ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    contracts.router,
    prefix="/contracts",
    tags=["Contracts"]
)

app.include_router(
    dashboard.router,
    prefix="/dashboard",
    tags=["Dashboard"]
)


@app.on_event("startup")
def startup():
    init_db()


@app.get("/")
def health_check():
    return {"message": "RiskLens-AI backend running"}
