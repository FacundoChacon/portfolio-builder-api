from fastapi import FastAPI

app = FastAPI(title="Portfolio Builder API")


@app.get("/")
def health() -> dict[str, str]:
    return {"status": "ok"}
