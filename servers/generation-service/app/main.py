from fastapi import FastAPI

app = FastAPI(title="generation-service")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
