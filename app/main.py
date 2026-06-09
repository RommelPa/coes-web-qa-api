from fastapi import FastAPI

app = FastAPI(
    title="COES Web QA API",
    description="Question-answering API over COES WebApi Mediciones documentation.",
    version="0.1.0",
)


@app.get("/")
def root() -> dict[str, str]:
    return {
        "message": "COES Web QA API is running",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}