from fastapi import FastAPI

app = FastAPI()


@app.get("/health")
async def health():
    return {
        "status": "ok"
    }


@app.get("/version")
async def version():
    return {
        "service": "portfolio-backend",
        "version": "1.0.0"
    }