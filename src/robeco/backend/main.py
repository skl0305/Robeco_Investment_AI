"""
Robeco Professional Investment Workbench - Main Server
Main FastAPI application entry point for the professional investment research platform
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .professional_api import setup_professional_routes
from ..core.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="Robeco Professional Investment Workbench",
    description="AI-powered institutional-grade investment research platform",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup professional routes
setup_professional_routes(app)

@app.on_event("startup")
async def startup():
    logger.info("🚀 Robeco Professional Investment Workbench starting up...")
    logger.info(f"📡 Server running on http://0.0.0.0:8001")
    logger.info(f"🔗 Professional Workbench: http://127.0.0.1:8001/workbench")
    logger.info(f"✅ System ready for institutional investment analysis")

@app.on_event("shutdown")
async def shutdown():
    logger.info("📴 Robeco Professional Investment Workbench shutting down...")

@app.get("/")
async def root():
    return {
        "message": "Robeco Professional Investment Workbench API",
        "status": "active",
        "version": "1.0.0",
        "workbench_url": "/workbench",
        "api_docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "robeco-professional-workbench",
        "unlimited_ai_capacity": True,
        "analysts_ready": 12
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=True)