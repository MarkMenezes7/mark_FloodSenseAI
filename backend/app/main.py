import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.limiter import limiter
from app.routes import weather, risk, alerts, rag, whatsapp
from app.db.database import create_tables
from app.services.alert_scheduler import start_scheduler, stop_scheduler

app = FastAPI(
    title="FloodSenseAI API",
    description="AI-Powered Flood Risk Prediction & Alert System",
    version="2.0.0"
)

# Rate limiter setup
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS — only allow our Vercel frontend (not all origins)
ALLOWED_ORIGINS = [
    "https://floodsenseai-frontend.vercel.app",
    "http://localhost:5173",   # local dev
    "http://localhost:3000",   # local dev alt
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Include routers
app.include_router(weather.router,   prefix="/api/weather",   tags=["Weather"])
app.include_router(risk.router,      prefix="/api/risk",      tags=["Flood Risk"])
app.include_router(alerts.router,    prefix="/api/alerts",    tags=["Alerts"])
app.include_router(rag.router,       prefix="/api/rag",       tags=["RAG Chatbot"])
app.include_router(whatsapp.router,  prefix="/api/whatsapp",  tags=["WhatsApp"])

@app.on_event("startup")
async def startup():
    # Database
    try:
        await create_tables()
        print("Database connected successfully")
    except Exception as e:
        print(f"Database connection failed: {e}")
        print("Server is running but DB features are disabled.")
        print("Check your DATABASE_URL in backend/.env and your internet connection.")

    # Scheduler — starts background alert checks every 30 min
    try:
        start_scheduler()
    except Exception as e:
        print(f"Scheduler failed to start: {e}")

@app.on_event("shutdown")
async def shutdown():
    stop_scheduler()

@app.get("/")
async def root():
    return {"message": "FloodSenseAI API is running", "status": "ok", "version": "2.0.0"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
