import logging

from config import config, validate_startup_config
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient

# Import routers so the lightweight app exposes the same API surface as server.py
from routes import ads, ai, auth, platforms

logger = logging.getLogger(__name__)

app = FastAPI(title="CrossPostMe API", version="1.0.0")

# CORS middleware with environment-specific configuration
cors_origins = config.get_cors_origins()
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
)

# Include the same routers used by server.py so /api/auth and others are available
app.include_router(ads.router)
app.include_router(platforms.router)
app.include_router(ai.router)
app.include_router(auth.router)

# Mongo client placeholder (closed on shutdown)
_client = None


@app.on_event("startup")
async def startup():
    """Initialize application components during startup."""
    global _client

    # Validate configuration before creating any connections
    validate_startup_config()
    logger.info("Configuration validated successfully")

    # Initialize MongoDB connection and attach to app.state so route dependencies work
    _client = AsyncIOMotorClient(config.get_mongo_url())
    app.state.db = _client[config.get_db_name()]
    logger.info(f"Connected to MongoDB database: {config.get_db_name()}")


@app.on_event("shutdown")
async def shutdown_db_client():
    """Clean up resources during shutdown."""
    global _client
    if _client:
        _client.close()
        logger.info("MongoDB connection closed")


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "crosspostme-api"}


@app.get("/")
async def root():
    return {"message": "CrossPostMe API - Ready for cross-platform posting!"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
