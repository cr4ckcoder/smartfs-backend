from fastapi import FastAPI
from .api import companies, works, accounts
from .core.config import settings
from .core.dependencies import init_db

app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

@app.on_event("startup")
async def on_startup():
    init_db()

@app.get("/health")
async def health():
    return {"status": "ok"}

app.include_router(companies.router, prefix="/companies", tags=["Companies"])
app.include_router(works.router, prefix="/works", tags=["Works"])
app.include_router(accounts.router, prefix="/accounts", tags=["Accounts"])
