import logging
import math
from datetime import datetime

# Import configuration and route modules
from config import config, validate_startup_config
from fastapi import APIRouter, Depends, FastAPI, HTTPException, Query
from models import (
    PaginatedStatusChecksResponse,
    PaginationInfo,
    StatusCheck,
    StatusCheckCreate,
)
from motor.motor_asyncio import AsyncIOMotorClient
from routes import ads, ai, auth, platforms
from starlette.middleware.cors import CORSMiddleware

# Global client variable for shutdown; database is stored on app.state
client = None

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Database dependency function


# Note: route modules should use routes.dependencies.get_db which reads from app.state
# The function above kept for backwards compatibility if imported elsewhere
async def get_db():
    if not hasattr(app.state, "db") or app.state.db is None:
        raise HTTPException(
            status_code=503,
            detail="Database connection not initialized. Server may be starting up.",
        )
    return app.state.db


# Add your routes to the router instead of directly to app
@api_router.get("/")
async def root():
    return {"message": "Hello World"}


@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate, database=Depends(get_db)):
    status_dict = input.model_dump()
    status_obj = StatusCheck(**status_dict)

    # Convert to dict and serialize datetime to ISO string for MongoDB
    doc = status_obj.model_dump()
    doc["timestamp"] = doc["timestamp"].isoformat()

    _ = await database.status_checks.insert_one(doc)
    return status_obj


@api_router.get("/status", response_model=PaginatedStatusChecksResponse)
async def get_status_checks(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    database=Depends(get_db),
):
    # Calculate pagination
    skip = (page - 1) * per_page
    total_items = await database.status_checks.count_documents({})
    total_pages = math.ceil(total_items / per_page)

    # Get paginated results, exclude MongoDB's _id field
    status_checks = (
        await database.status_checks.find({}, {"_id": 0})
        .sort("timestamp", -1)
        .skip(skip)
        .limit(per_page)
        .to_list(per_page)
    )

    # Convert ISO string timestamps back to datetime objects
    for check in status_checks:
        if isinstance(check["timestamp"], str):
            check["timestamp"] = datetime.fromisoformat(check["timestamp"])

    # Create pagination info
    pagination = PaginationInfo(
        page=page,
        per_page=per_page,
        total_items=total_items,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1,
    )

    return PaginatedStatusChecksResponse(
        items=[StatusCheck(**check) for check in status_checks], pagination=pagination
    )


# Include the router in the main app
app.include_router(api_router)

# Include marketplace system routers
app.include_router(ads.router)
app.include_router(platforms.router)
app.include_router(ai.router)
app.include_router(auth.router)

# Configure CORS middleware with validated origins
cors_origins = config.get_cors_origins()
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=cors_origins,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@app.on_event("startup")
async def startup():
    """Initialize application components during startup."""
    global client

    # Validate configuration before creating any connections
    validate_startup_config()
    logger.info("Configuration validated successfully")

    # Initialize MongoDB connection after validation and attach to app.state
    client = AsyncIOMotorClient(config.get_mongo_url())
    app.state.db = client[config.get_db_name()]
    logger.info(f"Connected to MongoDB database: {config.get_db_name()}")


@app.on_event("shutdown")
async def shutdown_db_client():
    """Clean up resources during shutdown."""
    if client:
        client.close()
        logger.info("MongoDB connection closed")
