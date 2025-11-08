import uuid
from datetime import datetime, timezone

from fastapi import APIRouter
from pydantic import BaseModel, Field

from db import get_typed_db

router = APIRouter(prefix="/api/diagrams", tags=["diagrams"])


class Diagram(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    mermaid: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DiagramCreate(BaseModel):
    title: str
    mermaid: str


@router.get("/", response_model=list[Diagram])
async def list_diagrams(skip: int = 0, limit: int = 100):
    """List diagrams with simple offset-based pagination.

    Params:
    - skip: number of documents to skip (offset)
    - limit: maximum number of documents to return (capped by max_limit)
    """
    db = get_typed_db()
    max_limit = 1000
    # enforce sane upper bound
    limit = max(limit, 0)
    limit = min(limit, max_limit)
    cursor = db.diagrams.find({}, {"_id": 0}).skip(int(skip)).limit(int(limit))
    docs = await cursor.to_list(length=int(limit))
    # convert created_at string to datetime if necessary
    for d in docs:
        if isinstance(d.get("created_at"), str):
            d["created_at"] = datetime.fromisoformat(d["created_at"])
    return docs


@router.post("/", response_model=Diagram)
async def create_diagram(payload: DiagramCreate):
    db = get_typed_db()
    obj = Diagram(title=payload.title, mermaid=payload.mermaid)
    doc = obj.model_dump()
    # ensure created_at is ISO string for storage
    doc["created_at"] = doc["created_at"].isoformat()
    await db.diagrams.insert_one(doc)
    return obj
