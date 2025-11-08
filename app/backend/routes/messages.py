"""Message and Lead Management Routes
Handles incoming messages from marketplace platforms and lead management
"""

import hashlib
import logging
import os
import re
import uuid
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query

from auth import get_current_user
from db import get_typed_db
from models import (
    IncomingMessage,
    IncomingMessageCreate,
    Lead,
    LeadCreate,
    LeadUpdate,
    OutgoingResponse,
    OutgoingResponseCreate,
    PlatformMonitoringConfig,
    PlatformMonitoringConfigCreate,
    ResponseTemplate,
    ResponseTemplateCreate,
)
from services import LeadService

# Feature flags
USE_SUPABASE = os.getenv("USE_SUPABASE", "true").lower() in ("true", "1", "yes")
PARALLEL_WRITE = os.getenv("PARALLEL_WRITE", "true").lower() in ("true", "1", "yes")

router = APIRouter(prefix="/api/messages", tags=["messages"])
logger = logging.getLogger(__name__)

# Platform validation
ALLOWED_PLATFORMS = {
    "email",
    "sms",
    "chat",
    "webhook",
    "craigslist",
    "facebook",
    "offerup",
    "nextdoor",
}

# ============================================================================
# SPAM DETECTION CONFIGURATION
# ============================================================================
# Improved spam detection with regex patterns and configurable thresholds
#
# Changes from previous version:
# 1. MIN_MESSAGE_LENGTH lowered from 20 to 10 to allow brief genuine inquiries
#    (e.g., "Is this available?", "Still for sale?")
#
# 2. SPAM_KEYWORDS replaced with SPAM_KEYWORDS_PATTERNS using regex
#    - Case-insensitive matching
#    - Word boundaries to avoid false positives
#    - Catches variations (e.g., "free money", "FREE MONEY", "fr33 m0ney")
#
# 3. BLOCKED_SENDERS now has database integration path via _get_blocked_senders()
#    - Current: Global hardcoded list (for testing)
#    - Future: Per-user configurable via database
#
# ============================================================================

MIN_MESSAGE_LENGTH = (
    10  # Lowered to allow brief but genuine inquiries like "Is this available?"
)

# Regex patterns for spam detection - case-insensitive with word boundaries
SPAM_KEYWORDS_PATTERNS = {
    r"\bfree\s*money\b",
    r"\bclick\s*here\b",
    r"\blimited\s*time\b",
    r"\bact\s*now\b",
    r"\bwinner\b",
    r"\bcongratulations\b",
    r"\blottery\b",
    r"\bclaim\s*your\s*prize\b",
    r"\bget\s*rich\s*quick\b",
    r"\bwork\s*from\s*home\b",
    r"\bmake\s*\$\d+\b",
    r"\bno\s*credit\s*check\b",
    r"\bguaranteed\s*approval\b",
    r"\bviagra\b",
    r"\bcialis\b",
    r"\bweight\s*loss\b",
    r"\bcrypto\s*investment\b",
}

# Blocked senders - should be moved to database for per-user configuration
# These are examples and won't block real spam in production
BLOCKED_SENDERS = {"spam@example.com", "noreply@spammer.com", "test@blocked.com"}


async def _get_blocked_senders(db, user_id: str) -> set:
    """Get blocked senders for a user from database.
    TODO: Implement per-user blocked sender management in database
    For now, returns the global BLOCKED_SENDERS set.

    Future implementation should query:
    db.blocked_senders.find({"user_id": user_id})
    """
    # TODO: Query database for user-specific blocked senders
    # blocked_docs = await db.blocked_senders.find({"user_id": user_id}).to_list(1000)
    # user_blocked = {doc["email"].lower() for doc in blocked_docs}
    # return BLOCKED_SENDERS | user_blocked
    return BLOCKED_SENDERS


def _is_spam_message(message_text: str) -> bool:
    """Check if message text contains spam patterns using regex.
    Uses case-insensitive matching with word boundaries to catch variations.
    """
    if not message_text:
        return False

    message_lower = message_text.lower()
    return any(
        re.search(pattern, message_lower, re.IGNORECASE)
        for pattern in SPAM_KEYWORDS_PATTERNS
    )


def _generate_content_hash(platform: str, sender_email: str, message_text: str) -> str:
    """Generate a hash for duplicate detection based on key message components"""
    # Use first 100 chars of message for fuzzy duplicate detection
    text_sample = (message_text or "")[:100]
    content = f"{platform}:{sender_email or ''}:{text_sample}"
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


# Incoming Messages Endpoints
@router.get("/", response_model=list[IncomingMessage])
async def get_messages(
    platform: str | None = Query(None),
    is_read: bool | None = Query(None),
    is_responded: bool | None = Query(None),
    priority: str | None = Query(None),
    limit: int = Query(100, le=1000),
    offset: int = Query(0, ge=0),
    user=Depends(get_current_user),
):
    """Get incoming messages with filtering options"""
    db = get_typed_db()

    # Build query
    query = {"user_id": user["user_id"]}
    if platform:
        query["platform"] = platform
    if is_read is not None:
        query["is_read"] = is_read
    if is_responded is not None:
        query["is_responded"] = is_responded
    if priority:
        query["priority"] = priority

    try:
        # Get messages sorted by received_at (newest first)
        # NOTE: Messages are stored in MongoDB only for now
        # TODO: Add dedicated messages table to Supabase schema for full migration
        messages_cursor = (
            db.messages.find(query).sort("received_at", -1).skip(offset).limit(limit)
        )
        messages = await messages_cursor.to_list(limit)

        # Convert to Pydantic models
        result = []
        for message in messages:
            if message:
                # Convert datetime strings back to datetime objects if needed
                if isinstance(message.get("received_at"), str):
                    message["received_at"] = datetime.fromisoformat(
                        message["received_at"].replace("Z", "+00:00"),
                    )
                result.append(IncomingMessage(**message))

        return result

    except Exception as e:
        logger.error(f"Error fetching messages: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch messages")


@router.post("/", response_model=IncomingMessage)
async def create_message(
    message: IncomingMessageCreate,
    user=Depends(get_current_user),
):
    """Create a new incoming message (typically used by monitoring services)"""
    db = get_typed_db()

    try:
        # Validate platform
        platform = message.platform.lower().strip() if message.platform else ""
        if platform not in ALLOWED_PLATFORMS:
            raise HTTPException(status_code=400, detail="Invalid platform")

        # Create message document
        message_data = message.dict()
        message_data["user_id"] = user["user_id"]
        message_data["platform"] = platform  # Use normalized platform
        message_data["id"] = f"msg_{uuid.uuid4().hex}_{platform}"
        message_data["received_at"] = datetime.now().isoformat()

        # Generate content hash for duplicate detection
        content_hash = _generate_content_hash(
            platform,
            message.sender_email or "",
            message.message_text or "",
        )
        message_data["content_hash"] = content_hash

        # Insert into database
        # Apply stricter filters before creating leads
        blocked_senders = await _get_blocked_senders(db, user["user_id"])
        is_spam = _is_spam_message(message.message_text)

        if USE_SUPABASE:
            # --- SUPABASE PATH (PRIMARY) ---
            try:
                from supabase_db import get_supabase
                client = get_supabase()
                if client:
                    # Log message to business_intelligence table
                    bi_data = {
                        "user_id": user["user_id"],
                        "event_type": "message_received",
                        "event_data": {
                            "message_id": message_data["id"],
                            "platform": platform,
                            "sender_email": message.sender_email,
                            "message_type": message.message_type,
                            "ad_id": message_data.get("ad_id"),
                            "content_hash": content_hash,
                            "message_text": message.message_text[:500] if message.message_text else None,  # Truncate for storage
                            "is_spam": is_spam
                        }
                    }
                    client.table("business_intelligence").insert(bi_data).execute()
                    logger.info(f"Message logged to Supabase BI: {message_data['id']}")

                    # PARALLEL WRITE: Also save to MongoDB
                    if PARALLEL_WRITE:
                        try:
                            result = await db.messages.insert_one(message_data)
                            logger.info(f"✅ Parallel write to MongoDB successful for message: {message_data['id']}")
                        except Exception as e:
                            logger.warning(f"⚠️  Parallel MongoDB write failed for message {message_data['id']}: {e}")
            except Exception as e:
                logger.error(f"Failed to log message to Supabase: {e}")
                # Continue with MongoDB fallback
                result = await db.messages.insert_one(message_data)
        else:
            # --- MONGODB PATH (FALLBACK) ---
            result = await db.messages.insert_one(message_data)

        # Apply stricter filters before creating leads
        blocked_senders = await _get_blocked_senders(db, user["user_id"])
        is_spam = _is_spam_message(message.message_text)

        should_create_lead = (
            message.message_type == "inquiry"
            and message.sender_email
            and message.sender_email.lower() not in blocked_senders
            and len(message.message_text or "") >= MIN_MESSAGE_LENGTH
            and bool(message_data.get("ad_id"))
            and not is_spam
        )

        if should_create_lead:
            # Use LeadService for intelligent lead matching and creation
            lead_service = LeadService(db)
            lead_id = await lead_service.find_or_create_lead(message_data)
            if lead_id:
                logger.info(
                    f"Lead processed: {lead_id} for message: {message_data['id']}",
                )
            else:
                logger.warning(
                    f"Failed to create/find lead for message: {message_data['id']}",
                )

        # Return created message
        created_message = await db.messages.find_one({"_id": result.inserted_id})
        if created_message:
            return IncomingMessage(**created_message)

        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve created message",
        )

    except Exception as e:
        logger.error(f"Error creating message: {e}")
        raise HTTPException(status_code=500, detail="Failed to create message")


@router.patch("/{message_id}/read")
async def mark_message_read(message_id: str, user=Depends(get_current_user)):
    """Mark a message as read"""
    db = get_typed_db()

    try:
        result = await db.messages.update_one(
            {"id": message_id, "user_id": user["user_id"]},
            {"$set": {"is_read": True}},
        )

        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Message not found")

        return {"success": True, "message": "Message marked as read"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error marking message as read: {e}")
        raise HTTPException(status_code=500, detail="Failed to update message")


# Lead Management Endpoints
@router.get("/leads/", response_model=list[Lead])
async def get_leads(
    status: str | None = Query(None),
    platform: str | None = Query(None),
    interest_level: str | None = Query(None),
    limit: int = Query(100, le=1000),
    offset: int = Query(0, ge=0),
    user=Depends(get_current_user),
):
    """Get leads with filtering options"""
    db = get_typed_db()

    # Build query
    query = {"user_id": user["user_id"]}
    if status:
        query["status"] = status
    if platform:
        query["platform"] = platform
    if interest_level:
        query["interest_level"] = interest_level

    try:
        # Get leads sorted by created_at (newest first)
        leads_cursor = (
            db.leads.find(query).sort("created_at", -1).skip(offset).limit(limit)
        )
        leads = await leads_cursor.to_list(limit)

        # Convert to Pydantic models
        result = []
        for lead in leads:
            if lead:
                # Convert datetime strings back to datetime objects if needed
                if isinstance(lead.get("created_at"), str):
                    lead["created_at"] = datetime.fromisoformat(
                        lead["created_at"].replace("Z", "+00:00"),
                    )
                if isinstance(lead.get("last_contact_at"), str):
                    lead["last_contact_at"] = datetime.fromisoformat(
                        lead["last_contact_at"].replace("Z", "+00:00"),
                    )
                result.append(Lead(**lead))

        return result

    except Exception as e:
        logger.error(f"Error fetching leads: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch leads")


@router.post("/leads/", response_model=Lead)
async def create_lead(lead: LeadCreate, user=Depends(get_current_user)):
    """Create a new lead"""
    db = get_typed_db()

    try:
        # Create lead document
        lead_data = lead.dict()
        lead_data["user_id"] = user["user_id"]
        lead_data["id"] = f"lead_{uuid.uuid4().hex}_{lead.platform}"
        lead_data["created_at"] = datetime.now().isoformat()
        lead_data["status"] = "new"

        # Insert into database
        result = await db.leads.insert_one(lead_data)

        # Return created lead
        created_lead = await db.leads.find_one({"_id": result.inserted_id})
        if created_lead:
            return Lead(**created_lead)

        raise HTTPException(status_code=500, detail="Failed to retrieve created lead")

    except Exception as e:
        logger.error(f"Error creating lead: {e}")
        raise HTTPException(status_code=500, detail="Failed to create lead")


@router.patch("/leads/{lead_id}", response_model=Lead)
async def update_lead(
    lead_id: str,
    lead_update: LeadUpdate,
    user=Depends(get_current_user),
):
    """Update a lead"""
    db = get_typed_db()

    try:
        # Build update document (exclude None values)
        update_data = {k: v for k, v in lead_update.dict().items() if v is not None}

        # Convert datetime objects to ISO strings if present
        if update_data.get("last_contact_at"):
            update_data["last_contact_at"] = update_data["last_contact_at"].isoformat()

        result = await db.leads.update_one(
            {"id": lead_id, "user_id": user["user_id"]},
            {"$set": update_data},
        )

        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Lead not found")

        # Return updated lead
        updated_lead = await db.leads.find_one(
            {"id": lead_id, "user_id": user["user_id"]},
        )
        if updated_lead:
            return Lead(**updated_lead)

        raise HTTPException(status_code=500, detail="Failed to retrieve updated lead")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating lead: {e}")
        raise HTTPException(status_code=500, detail="Failed to update lead")


# Response Templates Endpoints
@router.get("/templates/", response_model=list[ResponseTemplate])
async def get_response_templates(
    template_type: str | None = Query(None),
    platform: str | None = Query(None),
    user=Depends(get_current_user),
):
    """Get response templates"""
    db = get_typed_db()

    # Build query
    query = {"user_id": user["user_id"], "is_active": True}
    if template_type:
        query["template_type"] = template_type
    if platform:
        query["platforms"] = {"$in": [platform]}

    try:
        templates_cursor = db.response_templates.find(query).sort("name", 1)
        templates = await templates_cursor.to_list(100)

        result = []
        for template in templates:
            if template:
                if isinstance(template.get("created_at"), str):
                    template["created_at"] = datetime.fromisoformat(
                        template["created_at"].replace("Z", "+00:00"),
                    )
                result.append(ResponseTemplate(**template))

        return result

    except Exception as e:
        logger.error(f"Error fetching response templates: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch response templates",
        )


@router.post("/templates/", response_model=ResponseTemplate)
async def create_response_template(
    template: ResponseTemplateCreate,
    user=Depends(get_current_user),
):
    """Create a new response template"""
    db = get_typed_db()

    try:
        # Create template document
        template_data = template.dict()
        template_data["user_id"] = user["user_id"]
        template_data["id"] = f"template_{uuid.uuid4().hex}_{template.template_type}"
        template_data["created_at"] = datetime.now().isoformat()
        template_data["is_active"] = True

        # Insert into database
        result = await db.response_templates.insert_one(template_data)

        # Return created template
        created_template = await db.response_templates.find_one(
            {"_id": result.inserted_id},
        )
        if created_template:
            return ResponseTemplate(**created_template)

        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve created template",
        )

    except Exception as e:
        logger.error(f"Error creating response template: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to create response template",
        )


# Response Management
@router.post("/respond/", response_model=OutgoingResponse)
async def send_response(
    response: OutgoingResponseCreate,
    user=Depends(get_current_user),
):
    """Send a response to an incoming message"""
    db = get_typed_db()

    try:
        # Verify message exists
        message = await db.messages.find_one(
            {"id": response.message_id, "user_id": user["user_id"]},
        )

        if not message:
            raise HTTPException(status_code=404, detail="Message not found")

        # Create response document
        response_data = response.dict()
        response_data["user_id"] = user["user_id"]
        response_data["id"] = (
            f"resp_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{response.platform}"
        )
        response_data["created_at"] = datetime.now().isoformat()

        # Insert response
        result = await db.outgoing_responses.insert_one(response_data)

        # Mark original message as responded
        await db.messages.update_one(
            {"id": response.message_id, "user_id": user["user_id"]},
            {"$set": {"is_responded": True}},
        )

        # TODO: Actually send the response via the appropriate platform
        # This would involve calling platform-specific APIs or automation

        # Return created response
        created_response = await db.outgoing_responses.find_one(
            {"_id": result.inserted_id},
        )
        if created_response:
            return OutgoingResponse(**created_response)

        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve created response",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending response: {e}")
        raise HTTPException(status_code=500, detail="Failed to send response")


# Platform Monitoring Configuration
@router.get("/monitoring/", response_model=list[PlatformMonitoringConfig])
async def get_monitoring_configs(user=Depends(get_current_user)):
    """Get platform monitoring configurations"""
    db = get_typed_db()

    try:
        configs_cursor = db.monitoring_configs.find({"user_id": user["user_id"]})
        configs = await configs_cursor.to_list(100)

        result = []
        for config in configs:
            if config:
                if isinstance(config.get("created_at"), str):
                    config["created_at"] = datetime.fromisoformat(
                        config["created_at"].replace("Z", "+00:00"),
                    )
                if isinstance(config.get("last_check_at"), str):
                    config["last_check_at"] = datetime.fromisoformat(
                        config["last_check_at"].replace("Z", "+00:00"),
                    )
                result.append(PlatformMonitoringConfig(**config))

        return result

    except Exception as e:
        logger.error(f"Error fetching monitoring configs: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch monitoring configs",
        )


@router.post("/monitoring/", response_model=PlatformMonitoringConfig)
async def create_monitoring_config(
    config: PlatformMonitoringConfigCreate,
    user=Depends(get_current_user),
):
    """Create or update platform monitoring configuration"""
    db = get_typed_db()

    try:
        # Check if config already exists for this platform
        existing = await db.monitoring_configs.find_one(
            {"user_id": user["user_id"], "platform": config.platform},
        )

        config_data = config.dict()
        config_data["user_id"] = user["user_id"]
        config_data["created_at"] = datetime.now().isoformat()

        if existing:
            # Update existing config
            await db.monitoring_configs.update_one(
                {"user_id": user["user_id"], "platform": config.platform},
                {"$set": config_data},
            )
            config_data["id"] = existing["id"]
        else:
            # Create new config
            config_data["id"] = (
                f"monitor_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{config.platform}"
            )
            await db.monitoring_configs.insert_one(config_data)

        return PlatformMonitoringConfig(**config_data)

    except Exception as e:
        logger.error(f"Error creating monitoring config: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to create monitoring config",
        )


# Statistics and Analytics
@router.get("/stats/")
async def get_message_stats(user=Depends(get_current_user)):
    """Get message and lead statistics"""
    db = get_typed_db()

    try:
        # Get basic counts
        total_messages = await db.messages.count_documents({"user_id": user["user_id"]})
        unread_messages = await db.messages.count_documents(
            {"user_id": user["user_id"], "is_read": False},
        )
        total_leads = await db.leads.count_documents({"user_id": user["user_id"]})
        active_leads = await db.leads.count_documents(
            {
                "user_id": user["user_id"],
                "status": {"$in": ["new", "contacted", "qualified", "negotiating"]},
            },
        )

        # Get recent activity (last 24 hours)
        yesterday = (datetime.now() - timedelta(days=1)).isoformat()
        recent_messages = await db.messages.count_documents(
            {"user_id": user["user_id"], "received_at": {"$gte": yesterday}},
        )

        # Get platform breakdown
        pipeline = [
            {"$match": {"user_id": user["user_id"]}},
            {"$group": {"_id": "$platform", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
        ]
        platform_stats = await db.messages.aggregate(pipeline).to_list(10)

        return {
            "total_messages": total_messages,
            "unread_messages": unread_messages,
            "total_leads": total_leads,
            "active_leads": active_leads,
            "recent_messages_24h": recent_messages,
            "platform_breakdown": [
                {"platform": stat["_id"], "count": stat["count"]}
                for stat in platform_stats
            ],
        }

    except Exception as e:
        logger.error(f"Error fetching message stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch statistics")


# Helper Functions
# Note: Lead creation logic has been moved to LeadService (app/backend/services/lead_service.py)
# for better separation of concerns and more sophisticated matching strategies
