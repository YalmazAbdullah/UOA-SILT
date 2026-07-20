from fastapi import FastAPI

from server.api.routes import sessions, logs

app = FastAPI(title="Research Logger")

app.include_router(sessions.router)
app.include_router(logs.router)

@app.get("/")
def root():
    return {"status": "running"}