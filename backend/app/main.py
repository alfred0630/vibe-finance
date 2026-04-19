"""FastAPI entry point"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import parse, research

app = FastAPI(
    title="Vibe Finance",
    description="Natural language factor research API",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(parse.router, tags=["parse"])
app.include_router(research.router, tags=["research"])


@app.get("/")
def root():
    return {
        "service": "vibe-finance",
        "version": "0.1.0",
        "docs": "/docs",
    }


@app.get("/health")
def health():
    return {"status": "ok"}
