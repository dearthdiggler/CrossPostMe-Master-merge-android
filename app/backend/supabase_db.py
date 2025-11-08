"""
Supabase Database Connection
Replaces MongoDB with PostgreSQL via Supabase
"""

import os
from typing import Optional, Dict, List, Any
from supabase import create_client, Client
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

# 🔐 Get Supabase credentials from vault (with env fallback)
try:
    from vault import get_secret
    SUPABASE_URL = get_secret('supabase_url', os.getenv("SUPABASE_URL"))
    SUPABASE_SERVICE_KEY = get_secret('supabase_service_role_key', os.getenv("SUPABASE_SERVICE_KEY"))
except Exception as e:
    logger.warning(f"Could not load Supabase secrets from vault: {e}")
    # Fallback to environment variables
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
    logger.warning("SUPABASE_URL and SUPABASE_SERVICE_KEY not set - Supabase will not be available")
    SUPABASE_URL = None
    SUPABASE_SERVICE_KEY = None

# Initialize Supabase client (singleton)
_supabase_client: Optional[Client] = None

def get_supabase() -> Optional[Client]:
    """
    Get Supabase client instance (singleton pattern)

    Returns:
        Supabase client for database operations or None if not configured
    """
    global _supabase_client

    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        return None

    if _supabase_client is None:
        try:
            _supabase_client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
            logger.info("Supabase client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}")
            return None

    return _supabase_client


class SupabaseDB:
    """Wrapper class for Supabase operations with error handling"""

    def __init__(self):
        self.client = get_supabase()
        if not self.client:
            logger.warning("SupabaseDB initialized without client - operations will fail gracefully")

    def _check_client(self):
        """Check if client is available"""
        if not self.client:
            raise RuntimeError("Supabase client not initialized. Check SUPABASE_URL and SUPABASE_SERVICE_KEY")

    # ==================== USERS ====================

    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email"""
        self._check_client()
        try:
            response = self.client.table("users").select("*").eq("email", email).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error getting user by email: {e}")
            return None

    def get_user_by_username(self, username: str) -> Optional[Dict]:
        """Get user by username"""
        self._check_client()
        try:
            response = self.client.table("users").select("*").eq("username", username).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error getting user by username: {e}")
            return None

    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """Get user by ID"""
        self._check_client()
        try:
            response = self.client.table("users").select("*").eq("id", user_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error getting user by ID: {e}")
            return None

    def create_user(self, user_data: Dict) -> Optional[Dict]:
        """Create new user"""
        self._check_client()
        try:
            response = self.client.table("users").insert(user_data).execute()
            logger.info(f"User created: {user_data.get('email')}")
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            raise

    def update_user(self, user_id: str, updates: Dict) -> Optional[Dict]:
        """Update user"""
        self._check_client()
        try:
            response = self.client.table("users").update(updates).eq("id", user_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error updating user: {e}")
            return None

    def delete_user(self, user_id: str) -> bool:
        """Delete user (soft delete by setting is_active=false)"""
        self._check_client()
        try:
            self.client.table("users").update({"is_active": False}).eq("id", user_id).execute()
            return True
        except Exception as e:
            logger.error(f"Error deleting user: {e}")
            return False

    # ==================== BUSINESS PROFILES ====================

    def create_business_profile(self, profile_data: Dict) -> Optional[Dict]:
        """Create business profile"""
        self._check_client()
        try:
            response = self.client.table("user_business_profiles").insert(profile_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error creating business profile: {e}")
            raise

    def get_business_profile(self, user_id: str) -> Optional[Dict]:
        """Get business profile"""
        self._check_client()
        try:
            response = self.client.table("user_business_profiles").select("*").eq("user_id", user_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error getting business profile: {e}")
            return None

    def update_business_profile(self, user_id: str, updates: Dict) -> Optional[Dict]:
        """Update business profile"""
        self._check_client()
        try:
            response = self.client.table("user_business_profiles").update(updates).eq("user_id", user_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error updating business profile: {e}")
            return None

    # ==================== LISTINGS ====================

    def create_listing(self, listing_data: Dict) -> Optional[Dict]:
        """Create listing"""
        self._check_client()
        try:
            response = self.client.table("listings").insert(listing_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error creating listing: {e}")
            raise

    def get_listing(self, listing_id: str) -> Optional[Dict]:
        """Get listing by ID"""
        self._check_client()
        try:
            response = self.client.table("listings").select("*").eq("id", listing_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error getting listing: {e}")
            return None

    def get_user_listings(self, user_id: str, status: Optional[str] = None) -> List[Dict]:
        """Get all listings for user"""
        self._check_client()
        try:
            query = self.client.table("listings").select("*").eq("user_id", user_id)
            if status:
                query = query.eq("status", status)
            response = query.order("created_at", desc=True).execute()
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Error getting user listings: {e}")
            return []

    def update_listing(self, listing_id: str, updates: Dict) -> Optional[Dict]:
        """Update listing"""
        self._check_client()
        try:
            response = self.client.table("listings").update(updates).eq("id", listing_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error updating listing: {e}")
            return None

    def delete_listing(self, listing_id: str) -> bool:
        """Delete listing"""
        self._check_client()
        try:
            self.client.table("listings").delete().eq("id", listing_id).execute()
            return True
        except Exception as e:
            logger.error(f"Error deleting listing: {e}")
            return False

    # ==================== PLATFORM CONNECTIONS ====================

    def get_platform_connections(self, user_id: str) -> List[Dict]:
        """Get all platform connections for user"""
        self._check_client()
        try:
            response = self.client.table("platform_connections").select("*").eq("user_id", user_id).execute()
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Error getting platform connections: {e}")
            return []

    def get_platform_connection(self, user_id: str, platform: str) -> Optional[Dict]:
        """Get specific platform connection"""
        self._check_client()
        try:
            response = self.client.table("platform_connections")\
                .select("*")\
                .eq("user_id", user_id)\
                .eq("platform", platform)\
                .execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error getting platform connection: {e}")
            return None

    def upsert_platform_connection(self, connection_data: Dict) -> Optional[Dict]:
        """Create or update platform connection"""
        self._check_client()
        try:
            response = self.client.table("platform_connections").upsert(connection_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error upserting platform connection: {e}")
            raise

    # ==================== BUSINESS INTELLIGENCE ====================

    def log_event(self, user_id: str, event_type: str, event_data: Dict) -> Optional[Dict]:
        """Log business intelligence event"""
        self._check_client()
        try:
            response = self.client.table("business_intelligence").insert({
                "user_id": user_id,
                "event_type": event_type,
                "event_data": event_data
            }).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error logging event: {e}")
            return None

    def get_events(self, user_id: Optional[str] = None, event_type: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """Get business intelligence events"""
        self._check_client()
        try:
            query = self.client.table("business_intelligence").select("*")
            if user_id:
                query = query.eq("user_id", user_id)
            if event_type:
                query = query.eq("event_type", event_type)
            response = query.order("timestamp", desc=True).limit(limit).execute()
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Error getting events: {e}")
            return []

    # ==================== ANALYTICS ====================

    def get_industry_stats(self) -> List[Dict]:
        """Get industry breakdown (uses view)"""
        self._check_client()
        try:
            response = self.client.table("industry_breakdown").select("*").execute()
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Error getting industry stats: {e}")
            return []

    def get_user_stats(self, limit: int = 100) -> List[Dict]:
        """Get user statistics (uses view)"""
        self._check_client()
        try:
            response = self.client.table("user_stats").select("*").limit(limit).execute()
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Error getting user stats: {e}")
            return []

    def get_revenue_breakdown(self) -> Dict[str, int]:
        """Get revenue breakdown by range"""
        self._check_client()
        try:
            response = self.client.table("user_business_profiles")\
                .select("monthly_revenue")\
                .execute()

            breakdown = {}
            for row in response.data:
                revenue = row.get("monthly_revenue", "unknown")
                breakdown[revenue] = breakdown.get(revenue, 0) + 1

            return breakdown
        except Exception as e:
            logger.error(f"Error getting revenue breakdown: {e}")
            return {}

    # ==================== ANALYTICS TRACKING ====================

    def track_listing_view(self, listing_id: str, user_id: str, platform: str):
        """Track listing view"""
        self._check_client()
        try:
            # Upsert analytics record
            self.client.rpc("increment_listing_views", {
                "listing_id": listing_id,
                "platform_name": platform
            }).execute()
        except Exception as e:
            logger.error(f"Error tracking view: {e}")

    # ==================== UTILITY METHODS ====================

    def execute_raw_sql(self, sql: str, params: Optional[Dict] = None) -> Any:
        """Execute raw SQL query (use with caution)"""
        self._check_client()
        try:
            response = self.client.rpc("execute_sql", {"query": sql, "params": params or {}}).execute()
            return response.data
        except Exception as e:
            logger.error(f"Error executing raw SQL: {e}")
            raise


# Global instance
db = SupabaseDB()

# Export convenience function
def get_db() -> SupabaseDB:
    """Get database instance"""
    return db
