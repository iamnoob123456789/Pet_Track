from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRoute
from contextlib import asynccontextmanager
from datetime import datetime
import logging

# Import new models and services
from config.database import connect_to_mongo, close_mongo_connection
from services.image_similarity import image_similarity_engine
from services.hybrid_matching import hybrid_matching_engine
from services.notification_service import notification_service

# Import routes
from routes.auth import router as auth_router
from routes.pets import router as pets_router
from routes.matches import router as matches_router
from routes.contacts import router as contacts_router
from routes.notifications import router as notifications_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Pet-Track backend...")
    await connect_to_mongo()
    logger.info("Database connected successfully")
    
    # Initialize ML models
    logger.info("Loading ML models...")
    # Models are loaded when services are imported
    logger.info("ML models loaded successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Pet-Track backend...")
    await close_mongo_connection()
    logger.info("Database connection closed")

app = FastAPI(
    title="Pet-Track API",
    description="AI-powered pet identification and matching system",
    version="2.0.0",
    lifespan=lifespan
)

# Allow frontend origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Flutter web
        "http://localhost:8080",  # Vue.js
        "http://localhost:5000",
        "http://localhost:8000",
        "http://localhost:4200",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routes
app.include_router(auth_router, tags=["authentication"])
app.include_router(pets_router, tags=["pets"])
app.include_router(matches_router, tags=["matches"])
app.include_router(contacts_router, tags=["contacts"])
app.include_router(notifications_router, tags=["notifications"])

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Pet-Track API",
        "version": "2.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "Pet-Track API",
        "description": "AI-powered pet identification and matching system",
        "version": "2.0.0",
        "docs": "/docs",
        "health": "/health"
    }

@app.on_event("startup")
async def _log_routes():
    logger.info("Available routes:")
    for route in app.router.routes:
        if isinstance(route, APIRoute):
            logger.info(f"  PATH: {route.path}  METHODS: {sorted(route.methods)}")
    logger.info("API Documentation: http://localhost:8000/docs")

