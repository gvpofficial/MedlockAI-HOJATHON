from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.database.session import init_db, SessionLocal
from app.database.seed_data import seed_database
from app.api.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB & Seed demo data on startup
    init_db()
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Agentic Cross-Pharmacy Prescription Integrity System — Centralized Dispensing Ledger, Hard Rules, and Real-Time Multi-Agent Risk Engine.",
    version=settings.VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "system": settings.PROJECT_NAME,
        "version": settings.VERSION
    }


@app.get("/", tags=["Root"])
def root():
    return {
        "name": settings.PROJECT_NAME,
        "description": "Agentic Cross-Pharmacy Prescription Integrity System",
        "docs": "/docs",
        "api_v1": settings.API_V1_STR
    }
