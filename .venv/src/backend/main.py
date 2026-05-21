import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .routes import users, pharmacies, prescriptions, matching, stock, alerts

app = FastAPI(title="FieldScreen AI v2", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(pharmacies.router)
app.include_router(prescriptions.router)
app.include_router(matching.router)
app.include_router(stock.router)
app.include_router(alerts.router)


@app.get("/api/health")
async def health_check() -> dict:
    """Health check endpoint."""
    return {"status": "ok", "version": "0.1.0"}


_frontend_dir = os.path.join(os.path.dirname(__file__), "../frontend")
app.mount("/", StaticFiles(directory=_frontend_dir, html=True), name="frontend")
