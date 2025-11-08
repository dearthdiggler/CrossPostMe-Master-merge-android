"""Lead Service - Business logic for lead management and matching
Handles lead creation, matching, and updates with safer compound indexing
"""

import logging
import re
import uuid
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)

# Precompiled regex for strict domain validation
# - Each label: 1-63 chars, starts/ends with alphanumeric, can contain hyphens in middle
# - Labels separated by single dots (no consecutive dots)
# - TLD: 2-6 alphabetic characters (e.g., .com, .co.uk)
# - Total domain length: 4-253 characters
DOMAIN_PATTERN = re.compile(
    r"^(?=.{4,253}$)"  # Total length 4-253 chars
    r"(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)*"  # Zero or more subdomains
    r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\."  # Domain name
    r"[a-z]{2,6}$",  # TLD: 2-6 letters
)


class LeadService:
    """Service for managing leads with intelligent matching and deduplication"""

    def __init__(self, db):
        """Initialize LeadService with database connection

        Args:
            db: AsyncIOMotorDatabase instance

        """
        self.db = db

    async def find_or_create_lead(self, message_data: dict) -> str | None:
        """Find existing lead or create a new one from message data.
        Uses ordered matching strategy with compound indexes.

        Matching Strategy (in order of priority):
        1. Exact match: (user_id, platform, contact_email)
        2. Exact match: (user_id, platform, contact_phone)
        3. Fuzzy match: (user_id, platform, contact_name + contact_email) with confidence score

        Args:
            message_data: Dictionary containing message information

        Returns:
            Lead ID (str) if successful, None if creation failed

        """
        try:
            user_id = message_data.get("user_id")
            platform = message_data.get("platform")
            sender_email = message_data.get("sender_email")
            sender_phone = message_data.get("sender_phone")
            sender_name = message_data.get("sender_name")

            if not user_id or not platform:
                logger.warning("Missing user_id or platform in message_data")
                return None

            # Strategy 1: Exact email match (highest priority)
            if sender_email:
                existing_lead = await self.db.leads.find_one(
                    {
                        "user_id": user_id,
                        "platform": platform,
                        "contact_email": sender_email,
                    },
                )

                if existing_lead:
                    logger.info(f"Found existing lead by email: {existing_lead['id']}")
                    lead_id = str(existing_lead["id"]) if existing_lead.get("id") else None
                    await self._update_lead_last_contact(
                        lead_id,
                        message_data,
                    )
                    return lead_id

            # Strategy 2: Exact phone match
            if sender_phone:
                existing_lead = await self.db.leads.find_one(
                    {
                        "user_id": user_id,
                        "platform": platform,
                        "contact_phone": sender_phone,
                    },
                )

                if existing_lead:
                    logger.info(f"Found existing lead by phone: {existing_lead['id']}")
                    lead_id = str(existing_lead["id"]) if existing_lead.get("id") else None
                    await self._update_lead_last_contact(
                        lead_id,
                        message_data,
                    )
                    return lead_id

            # Strategy 3: Fuzzy match by name + email (if both available)
            if sender_name and sender_email:
                confidence_score, fuzzy_lead = await self._fuzzy_match_lead(
                    user_id,
                    platform,
                    sender_name,
                    sender_email,
                )

                if fuzzy_lead and confidence_score >= 0.8:  # 80% confidence threshold
                    logger.info(
                        f"Found existing lead by fuzzy match (confidence: {confidence_score}): {fuzzy_lead['id']}",
                    )
                    lead_id = str(fuzzy_lead["id"]) if fuzzy_lead.get("id") else None
                    await self._update_lead_last_contact(lead_id, message_data)
                    return lead_id

            # No match found - create new lead
            lead_id = await self._create_new_lead(message_data)
            logger.info(f"Created new lead: {lead_id}")
            return lead_id

        except Exception as e:
            logger.error(f"Error in find_or_create_lead: {e}", exc_info=True)
            return None

    async def update_lead_from_message(self, lead_id: str, message_data: dict) -> bool:
        """Update an existing lead with information from a new message

        Args:
            lead_id: ID of the lead to update
            message_data: Dictionary containing message information

        Returns:
            True if successful, False otherwise

        """
        try:
            update_fields = {
                "last_contact_at": message_data.get(
                    "received_at",
                    datetime.now().isoformat(),
                ),
            }

            # Update contact info if provided and not already set
            existing_lead = await self.db.leads.find_one({"id": lead_id})
            if not existing_lead:
                logger.warning(f"Lead not found: {lead_id}")
                return False

            # Fill in missing contact information
            if message_data.get("sender_email") and not existing_lead.get(
                "contact_email",
            ):
                update_fields["contact_email"] = message_data["sender_email"]

            if message_data.get("sender_phone") and not existing_lead.get(
                "contact_phone",
            ):
                update_fields["contact_phone"] = message_data["sender_phone"]

            if message_data.get("sender_name") and not existing_lead.get(
                "contact_name",
            ):
                update_fields["contact_name"] = message_data["sender_name"]

            # Add message ID to interaction history
            if "message_ids" not in existing_lead:
                update_fields["message_ids"] = []

            result = await self.db.leads.update_one(
                {"id": lead_id},
                {
                    "$set": update_fields,
                    "$addToSet": {"message_ids": message_data.get("id")},
                },
            )

            return bool(result.modified_count > 0)

        except Exception as e:
            logger.error(f"Error updating lead {lead_id}: {e}", exc_info=True)
            return False

    async def _update_lead_last_contact(self, lead_id: str | None, message_data: dict) -> None:
        """Update the last_contact_at timestamp for an existing lead"""
        if lead_id is None:
            logger.warning("Cannot update lead last contact: lead_id is None")
            return

        try:
            await self.db.leads.update_one(
                {"id": lead_id},
                {
                    "$set": {
                        "last_contact_at": message_data.get(
                            "received_at",
                            datetime.now().isoformat(),
                        ),
                    },
                    "$addToSet": {"message_ids": message_data.get("id")},
                },
            )
        except Exception as e:
            logger.error(f"Error updating lead last contact: {e}", exc_info=True)

    async def _create_new_lead(self, message_data: dict) -> str:
        """Create a new lead from message data

        Returns:
            Lead ID of the newly created lead

        """
        lead_id = f"lead_{uuid.uuid4().hex}_{message_data['platform']}"

        lead_data = {
            "id": lead_id,
            "user_id": message_data["user_id"],
            "ad_id": message_data.get("ad_id"),
            "platform": message_data["platform"],
            "contact_name": message_data.get("sender_name"),
            "contact_email": message_data.get("sender_email"),
            "contact_phone": message_data.get("sender_phone"),
            "interest_level": "medium",  # Default for inquiries
            "status": "new",
            "source_message_id": message_data["id"],
            "message_ids": [message_data["id"]],
            "last_contact_at": message_data.get(
                "received_at",
                datetime.now().isoformat(),
            ),
            "created_at": message_data.get("received_at", datetime.now().isoformat()),
            "notes": f"Initial inquiry: {message_data.get('message_text', '')[:100]}...",
            "tags": ["auto-created", "inquiry"],
        }

        await self.db.leads.insert_one(lead_data)
        return lead_id

    async def _fuzzy_match_lead(
        self,
        user_id: str,
        platform: str,
        name: str,
        email: str,
    ) -> tuple[float, dict[Any, Any] | None]:
        """Perform fuzzy matching on leads by name and email similarity

        Args:
            user_id: User ID
            platform: Platform name
            name: Contact name to match
            email: Contact email to match

        Returns:
            Tuple of (confidence_score, lead_document or None)
            confidence_score is between 0.0 and 1.0

        """
        try:
            # Find leads with similar names on the same platform
            potential_leads = await self.db.leads.find(
                {
                    "user_id": user_id,
                    "platform": platform,
                    "contact_name": {"$exists": True, "$ne": None},
                },
            ).to_list(100)

            best_match = None
            best_score = 0.0

            for lead in potential_leads:
                score = self._calculate_match_confidence(
                    name,
                    email,
                    lead.get("contact_name", ""),
                    lead.get("contact_email", ""),
                )

                if score > best_score:
                    best_score = score
                    best_match = lead

            return best_score, best_match

        except Exception as e:
            logger.error(f"Error in fuzzy matching: {e}", exc_info=True)
            return 0.0, None

    def _calculate_match_confidence(
        self,
        name1: str,
        email1: str,
        name2: str,
        email2: str,
    ) -> float:
        """Calculate confidence score for matching two contacts

        Uses weighted scoring:
        - Email domain match: 40%
        - Name similarity: 60%

        Returns:
            Confidence score between 0.0 and 1.0

        """
        score = 0.0

        # Email domain matching (40% weight)
        if email1 and email2:
            domain1 = self._extract_email_domain(email1)
            domain2 = self._extract_email_domain(email2)
            if domain1 and domain2 and domain1 == domain2:
                score += 0.4

        # Name similarity (60% weight)
        if name1 and name2:
            name1_lower = name1.lower().strip()
            name2_lower = name2.lower().strip()

            # Exact match
            if name1_lower == name2_lower:
                score += 0.6
            # One contains the other (partial match)
            elif name1_lower in name2_lower or name2_lower in name1_lower:
                score += 0.4
            # First/last name swap or similar
            elif self._names_similar(name1_lower, name2_lower):
                score += 0.3

        return score

    def _names_similar(self, name1: str, name2: str) -> bool:
        """Check if names are similar (handles first/last name swaps)

        Examples:
        - "John Doe" and "Doe John" -> True
        - "John D" and "John Doe" -> True

        """
        parts1 = set(name1.split())
        parts2 = set(name2.split())

        # If any part matches, consider similar
        return len(parts1 & parts2) > 0

    def _extract_email_domain(self, email: str) -> str:
        """Safely extract and normalize domain from email address

        Args:
            email: Email address string

        Returns:
            Normalized domain string if valid, empty string if invalid

        Examples:
            "user@example.com" -> "example.com"
            "user@sub.example.com" -> "sub.example.com"
            "notanemail" -> ""
            "user@@domain.com" -> ""
            "" -> ""

        """
        if not email or not isinstance(email, str):
            return ""

        # Trim and normalize
        email = email.strip().lower()

        # Check for exactly one '@' symbol
        if email.count("@") != 1:
            return ""

        # Use partition to safely split
        _, _, domain = email.partition("@")

        # Validate domain part with strict pattern
        if not domain:
            return ""

        # Use precompiled regex for comprehensive domain validation
        # Ensures proper structure: labels, dots, TLD requirements
        if not DOMAIN_PATTERN.match(domain):
            return ""

        return domain

    async def ensure_indexes(self) -> None:
        """Ensure compound indexes exist for efficient lead matching
        Should be called during application startup or migration
        """
        try:
            # Compound index for exact email matching
            await self.db.leads.create_index(
                [("user_id", 1), ("platform", 1), ("contact_email", 1)],
                name="leads_email_match_idx",
                background=True,
            )

            # Compound index for exact phone matching
            await self.db.leads.create_index(
                [("user_id", 1), ("platform", 1), ("contact_phone", 1)],
                name="leads_phone_match_idx",
                background=True,
            )

            # Index for fuzzy name matching
            await self.db.leads.create_index(
                [("user_id", 1), ("platform", 1), ("contact_name", 1)],
                name="leads_name_match_idx",
                background=True,
            )

            logger.info("Lead service indexes ensured")

        except Exception as e:
            logger.error(f"Error ensuring lead indexes: {e}", exc_info=True)
