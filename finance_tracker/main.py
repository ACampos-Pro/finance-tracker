from contextlib import asynccontextmanager

from fastapi import FastAPI

from . import models
from .database import engine
from .routers import summary, transactions


@asynccontextmanager
async def lifespan(app: FastAPI):
    models.Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Finance Tracker API",
    description=(
        "Track personal income and expenses with category breakdowns and summaries. "
        "Visit `/docs` for the interactive Swagger UI."
    ),
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(transactions.router)
app.include_router(summary.router)


@app.get("/", tags=["health"])
def root():
    return {"status": "ok", "message": "Finance Tracker API is running"}
