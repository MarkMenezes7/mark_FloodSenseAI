from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import weather, risk, alerts, rag, whatsapp
from app.db.database import create_tables
from app.services.alert_scheduler import start_scheduler, stop_scheduler

app = FastAPI(
    title="FloodSenseAI API",
    description="AI-Powered Flood Risk Prediction & Alert System",
    version="2.0.0"
)

# CORS — allow frontend to call backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
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
