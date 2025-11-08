import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


# Platform Account Models
class PlatformAccount(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    platform: str  # facebook, craigslist, offerup, nextdoor
    account_name: str
    account_email: str
    status: str = "active"  # active, suspended, flagged
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_used: Optional[datetime] = None


class PlatformAccountCreate(BaseModel):
    platform: str
    account_name: str
    account_email: str


# Ad Models
class Ad(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    price: float
    category: str
    location: str
    images: List[str] = []
    platforms: List[str] = []  # Which platforms to post to
    owner_id: Optional[str] = None
    status: str = "draft"  # draft, scheduled, posted, paused
    created_at: datetime = Field(default_factory=datetime.utcnow)
    scheduled_time: Optional[datetime] = None
    auto_renew: bool = False


class AdCreate(BaseModel):
    title: str
    description: str
    price: float
    category: str
    location: str
    images: List[str] = []
    platforms: List[str] = []
    owner_id: Optional[str] = None
    scheduled_time: Optional[datetime] = None
    auto_renew: bool = False


class AdUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    category: Optional[str] = None
    location: Optional[str] = None
    images: Optional[List[str]] = None
    platforms: Optional[List[str]] = None
    status: Optional[str] = None
    scheduled_time: Optional[datetime] = None
    auto_renew: Optional[bool] = None


# Posted Ad Models
class PostedAd(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    ad_id: str
    platform: str
    platform_ad_id: Optional[str] = None
    post_url: Optional[str] = None
    posted_at: datetime = Field(default_factory=datetime.utcnow)
    status: str = "active"  # active, expired, removed, flagged
    views: int = 0
    clicks: int = 0
    leads: int = 0
    metrics: Dict[str, Any] = Field(default_factory=dict)


class PostedAdCreate(BaseModel):
    ad_id: str
    platform: str
    platform_ad_id: Optional[str] = None
    post_url: Optional[str] = None
    metrics: Optional[Dict[str, Any]] = None


# Analytics Models
class AdAnalytics(BaseModel):
    ad_id: str
    platform: str
    views: int = 0
    clicks: int = 0
    leads: int = 0
    messages: int = 0
    conversion_rate: float = 0.0
    date: datetime = Field(default_factory=datetime.utcnow)


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
    suggested_categories: List[str]
    keywords: List[str]


# Pagination Models
class PaginationInfo(BaseModel):
    page: int
    per_page: int
    total_items: int
    total_pages: int
    has_next: bool
    has_prev: bool


class PaginatedAdsResponse(BaseModel):
    items: List[Ad]
    pagination: PaginationInfo


class PaginatedPostedAdsResponse(BaseModel):
    items: List[PostedAd]
    pagination: PaginationInfo


# Status Check Models
class StatusCheck(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class StatusCheckCreate(BaseModel):
    client_name: str


class PaginatedStatusChecksResponse(BaseModel):
    items: List[StatusCheck]
    pagination: PaginationInfo


# User model for simple auth
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class UserCreate(BaseModel):
    email: str
    password: str
