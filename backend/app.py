from fastapi import FastAPI
from backend.routes import router

app = FastAPI(title="CardioTwin AI", version="1.0.0")
app.include_router(router)
