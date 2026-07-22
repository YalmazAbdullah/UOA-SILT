from fastapi import FastAPI

from server.api.routes import log, session


app = FastAPI(title="Research Logger")

app.include_router(session.router)
app.include_router(log.router)

@app.get("/")
def root():
    return {"status": "running"}