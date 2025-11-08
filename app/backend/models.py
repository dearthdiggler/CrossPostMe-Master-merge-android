import uuid
from datetime import datetime, timezone

from pydantic import BaseModel, Field


# Platform Account Models
class PlatformAccount(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = "default"  # User identifier for multi-tenant support
    platform: str  # facebook, craigslist, offerup, nextdoor
    account_name: str
    account_email: str
    status: str = "active"  # active, suspended, flagged
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_used: datetime | None = None


class PlatformAccountCreate(BaseModel):
    platform: str
    account_name: str
    account_email: str


# Ad Models
class Ad(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = "default"  # User identifier for multi-tenant support
    title: str
    description: str
    price: float
    category: str
    location: str
    images: list[str] = []
    platforms: list[str] = []  # Which platforms to post to
    status: str = "draft"  # draft, scheduled, posted, paused
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    scheduled_time: datetime | None = None
    auto_renew: bool = False


class AdCreate(BaseModel):
    user_id: str = "default"  # User identifier for multi-tenant support
    title: str
    description: str
    price: float
    category: str
    location: str
    images: list[str] = []
    platforms: list[str] = []
    scheduled_time: datetime | None = None
    auto_renew: bool = False


class AdUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    price: float | None = None
    category: str | None = None
    location: str | None = None
    images: list[str] | None = None
    platforms: list[str] | None = None
    status: str | None = None
    scheduled_time: datetime | None = None
    auto_renew: bool | None = None


# Posted Ad Models
class PostedAd(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    ad_id: str
    platform: str
    platform_ad_id: str | None = None
    post_url: str | None = None
    posted_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: str = "active"  # active, expired, removed, flagged
    views: int = 0
    clicks: int = 0
    leads: int = 0


class PostedAdCreate(BaseModel):
    ad_id: str
    platform: str
    platform_ad_id: str | None = None
    post_url: str | None = None


# Analytics Models
class AdAnalytics(BaseModel):
    ad_id: str
    platform: str
    views: int = 0
    clicks: int = 0
    leads: int = 0
    messages: int = 0
    conversion_rate: float = 0.0
    date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DashboardStats(BaseModel):
    total_ads: int
    active_ads: int
    total_posts: int
    total_views: int
    total_leads: int
    platforms_connected: int


# AI Generation Models
class AIAdRequest(BaseModel):
    product_name: str
    product_details: str
    price: float
    category: str
    tone: str = "professional"  # professional, casual, urgent


class AIAdResponse(BaseModel):
    title: str
    description: str
    suggested_categories: list[str]
    keywords: list[str]


# Incoming Message Models
class IncomingMessage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = "default"  # User identifier for multi-tenant support
    ad_id: str | None = None  # Which ad this message relates to
    platform: str  # facebook, craigslist, offerup, nextdoor
    platform_message_id: str | None = None  # Platform's internal message ID
    sender_name: str | None = None
    sender_email: str | None = None
    sender_phone: str | None = None
    sender_profile_url: str | None = None
    subject: str | None = None
    message_text: str
    message_type: str = "inquiry"  # inquiry, offer, question, complaint
    source_type: str = "platform"  # platform, email, parsed_notification
    received_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_read: bool = False
    is_responded: bool = False
    priority: str = "normal"  # low, normal, high, urgent
    raw_data: dict | None = None  # Store original platform data


class IncomingMessageCreate(BaseModel):
    ad_id: str | None = None
    platform: str
    platform_message_id: str | None = None
    sender_name: str | None = None
    sender_email: str | None = None
    sender_phone: str | None = None
    sender_profile_url: str | None = None
    subject: str | None = None
    message_text: str
    message_type: str = "inquiry"
    source_type: str = "platform"
    priority: str = "normal"
    raw_data: dict | None = None


# Lead Management Models
class Lead(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = "default"
    ad_id: str | None = None
    platform: str
    contact_name: str | None = None
    contact_email: str | None = None
    contact_phone: str | None = None
    interest_level: str = "unknown"  # unknown, low, medium, high, very_high
    status: str = "new"  # new, contacted, qualified, negotiating, sold, lost
    source_message_id: str | None = None  # First message that created this lead
    last_contact_at: datetime | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    notes: str | None = None
    estimated_value: float | None = None
    tags: list[str] = []


class LeadCreate(BaseModel):
    ad_id: str | None = None
    platform: str
    contact_name: str | None = None
    contact_email: str | None = None
    contact_phone: str | None = None
    interest_level: str = "unknown"
    source_message_id: str | None = None
    notes: str | None = None
    estimated_value: float | None = None
    tags: list[str] = []


class LeadUpdate(BaseModel):
    contact_name: str | None = None
    contact_email: str | None = None
    contact_phone: str | None = None
    interest_level: str | None = None
    status: str | None = None
    last_contact_at: datetime | None = None
    notes: str | None = None
    estimated_value: float | None = None
    tags: list[str] | None = None


# Response Templates
class ResponseTemplate(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = "default"
    name: str
    subject: str | None = None
    template_text: str
    template_type: str = (
        "general"  # general, price_inquiry, availability, meeting_request
    )
    platforms: list[str] = []  # Which platforms this template is suitable for
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ResponseTemplateCreate(BaseModel):
    name: str
    subject: str | None = None
    template_text: str
    template_type: str = "general"
    platforms: list[str] = []


# Outgoing Response Models
class OutgoingResponse(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = "default"
    message_id: str  # Which incoming message this responds to
    lead_id: str | None = None
    platform: str
    response_text: str
    response_method: str = "platform"  # platform, email, sms
    sent_at: datetime | None = None
    delivery_status: str = "pending"  # pending, sent, delivered, failed
    template_used: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class OutgoingResponseCreate(BaseModel):
    message_id: str
    lead_id: str | None = None
    platform: str
    response_text: str
    response_method: str = "platform"
    template_used: str | None = None


# Email Monitoring Models
class EmailRule(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = "default"
    platform: str
    sender_pattern: str  # Email pattern to match (e.g., "*@craigslist.org")
    subject_patterns: list[str] = (
        []
    )  # Subject line patterns to identify platform notifications
    parsing_rules: dict = {}  # Rules for extracting data from email content
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class EmailRuleCreate(BaseModel):
    platform: str
    sender_pattern: str
    subject_patterns: list[str] = []
    parsing_rules: dict = {}


# Platform Monitoring Config
class PlatformMonitoringConfig(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = "default"
    platform: str
    monitoring_enabled: bool = True
    check_interval_minutes: int = 15  # How often to check for new messages
    email_monitoring: bool = True
    platform_scraping: bool = True  # Direct platform message scraping
    last_check_at: datetime | None = None
    credentials_id: str | None = None  # Reference to stored credentials
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PlatformMonitoringConfigCreate(BaseModel):
    platform: str
    monitoring_enabled: bool = True
    check_interval_minutes: int = 15
    email_monitoring: bool = True
    platform_scraping: bool = True
    credentials_id: str | None = None
