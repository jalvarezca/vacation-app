"""Vacation Planning App - API REST (FastAPI).

Correr con:  uvicorn app.main:app --reload
Documentación interactiva del API:  http://localhost:8000/docs
"""
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine
from .routers import admin, auth, catalogs, requests

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Vacation Planning App", version="0.1.0")

# En desarrollo permite el React local; en producción (Render) se define
# CORS_ORIGINS con la URL del frontend, o "*" para pruebas abiertas.
_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials="*" not in _origins,  # con "*" el navegador exige credentials=False
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(requests.router)
app.include_router(admin.router)
app.include_router(catalogs.router)


@app.get("/")
def root():
    return {"app": "Vacation Planning App", "docs": "/docs"}
