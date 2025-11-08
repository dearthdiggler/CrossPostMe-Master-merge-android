"""Email Monitoring Service
Monitors a dedicated email account for marketplace notifications and parses them into structured messages
"""

import asyncio
import email
import hashlib
import imaplib
import logging
import re
import uuid
from datetime import datetime
from typing import Any, ClassVar

from ..db import get_typed_db
from ..models import EmailRule, IncomingMessageCreate

logger = logging.getLogger(__name__)


class EmailMonitoringService:
    """Service to monitor email for marketplace notifications"""

    # Message classification keywords
    PRICE_KEYWORDS: ClassVar[tuple[str, ...]] = ("price", "how much", "cost", "$")
    AVAILABILITY_KEYWORDS: ClassVar[tuple[str, ...]] = (
        "available",
        "still have",
        "sold",
    )
    MEETING_KEYWORDS: ClassVar[tuple[str, ...]] = ("meet", "pickup", "when", "where")
    INTEREST_KEYWORDS: ClassVar[tuple[str, ...]] = ("interested", "want", "buy")

    # Priority keywords
    HIGH_PRIORITY_KEYWORDS: ClassVar[tuple[str, ...]] = (
        "urgent",
        "asap",
        "immediately",
        "cash",
        "today",
    )
    NORMAL_PRIORITY_KEYWORDS: ClassVar[tuple[str, ...]] = (
        "interested",
        "buy",
        "purchase",
        "take it",
    )

    # Default parsing rules for different platforms
    default_parsing_rules: ClassVar[dict[str, dict[str, Any]]] = {}

    def __init__(self, email_config: dict):
        self.email_config = email_config
        self.is_running = False

    def _generate_content_hash(
        self,
        platform: str,
        sender_email: str,
        message_text: str,
    ) -> str:
        """Generate a hash for duplicate detection based on key message components"""
        # Use first 100 chars of message for fuzzy duplicate detection
        text_sample = (message_text or "")[:100]
        content = f"{platform}:{sender_email or ''}:{text_sample}"
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

        # Default parsing rules for different platforms
        self.default_parsing_rules = {
            "craigslist": {
                "sender_patterns": ["*@craigslist.org", "noreply@craigslist.org"],
                "subject_patterns": [
                    r"Reply to your (.+) ad",
                    r"New reply to your ad",
                    r"CL: (.+) - (.+)",
                ],
                "message_extractors": {
                    "sender_email": r"From: (.+@.+)",
                    "sender_name": r"From: (.+?) <",
                    "ad_title": r"Reply to your (.+) ad",
                    "original_message": r"Reply:\s*(.+?)(?:\n\n|$)",
                },
            },
            "facebook": {
                "sender_patterns": ["*@facebookmail.com", "*@facebook.com"],
                "subject_patterns": [
                    r"(.+) sent you a message about (.+)",
                    r"New message about your listing",
                    r"FB Marketplace: (.+)",
                ],
                "message_extractors": {
                    "sender_name": r"(.+) sent you a message",
                    "ad_title": r"message about (.+)",
                    "message_preview": r"Message:\s*(.+?)(?:\n|$)",
                },
            },
            "offerup": {
                "sender_patterns": ["*@offerup.com", "notifications@offerup.com"],
                "subject_patterns": [
                    r"(.+) sent you a message",
                    r"New message from (.+)",
                    r"Message about (.+)",
                ],
                "message_extractors": {
                    "sender_name": r"(.+) sent you a message",
                    "message_text": r"Message:\s*(.+?)(?:\n|View|Reply)",
                },
            },
        }

    async def start_monitoring(self):
        """Start the email monitoring service"""
        self.is_running = True
        logger.info("Starting email monitoring service")

        while self.is_running:
            try:
                await self._check_new_emails()
                await asyncio.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Error in email monitoring loop: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes on error

    def stop_monitoring(self):
        """Stop the email monitoring service"""
        self.is_running = False
        logger.info("Email monitoring service stopped")

    async def _check_new_emails(self):
        """Check for new emails and process them"""
        imap_server = None
        try:
            # Connect to IMAP server
            imap_server = imaplib.IMAP4_SSL(
                self.email_config["imap_server"],
                self.email_config["imap_port"],
            )

            # Login
            imap_server.login(self.email_config["email"], self.email_config["password"])

            # Select inbox
            imap_server.select("INBOX")

            # Search for unread emails
            _, message_ids = imap_server.search(None, "UNSEEN")

            if message_ids[0]:
                for msg_id in message_ids[0].split():
                    await self._process_email(msg_id, imap_server)

            # Close connection
            imap_server.close()
            imap_server.logout()

        except Exception as e:
            logger.error(f"Error checking emails: {e}")
            if imap_server:
                try:
                    imap_server.logout()
                except Exception as cleanup_err:
                    logger.error(
                        f"Failed to logout from IMAP server during cleanup: {cleanup_err}",
                        exc_info=True,
                    )

    async def _process_email(self, msg_id: bytes, imap_server):
        """Process a single email message"""
        try:
            # Fetch email
            _, msg_data = imap_server.fetch(msg_id.decode(), "(RFC822)")
            email_message = email.message_from_bytes(msg_data[0][1])

            # Extract basic email info
            sender = email_message.get("From", "")
            subject = email_message.get("Subject", "")
            email_message.get("Date", "")

            # Get email body
            body = self._extract_email_body(email_message)

            # Determine platform and parse message
            platform = self._identify_platform(sender, subject)
            if platform:
                parsed_message = await self._parse_platform_message(
                    platform,
                    sender,
                    subject,
                    body,
                    email_message,
                )

                if parsed_message:
                    # Store in database
                    await self._store_incoming_message(parsed_message)

                    # Mark email as read
                    imap_server.store(msg_id.decode(), "+FLAGS", "\\Seen")

                    logger.info(f"Processed {platform} email: {subject}")

        except Exception as e:
            try:
                mid = msg_id.decode()
            except Exception:
                mid = repr(msg_id)
            logger.error(f"Error processing email {mid}: {e}")

    def _extract_email_body(self, email_message) -> str:
        """Extract plain text body from email message"""
        if email_message.is_multipart():
            for part in email_message.walk():
                content_type = part.get_content_type()
                if content_type == "text/plain":
                    payload = part.get_payload(decode=True)
                    return str(payload.decode("utf-8", errors="ignore")) if payload else ""
        else:
            payload = email_message.get_payload(decode=True)
            return str(payload.decode("utf-8", errors="ignore")) if payload else ""
        return ""

    def _identify_platform(self, sender: str, subject: str) -> str | None:
        """Identify which platform the email is from"""
        sender_lower = sender.lower()
        subject_lower = subject.lower()

        # Check against known patterns
        if any(pattern in sender_lower for pattern in ["craigslist.org"]):
            return "craigslist"
        if any(pattern in sender_lower for pattern in ["facebook", "facebookmail"]):
            return "facebook"
        if any(pattern in sender_lower for pattern in ["offerup.com"]):
            return "offerup"
        if any(pattern in sender_lower for pattern in ["nextdoor"]):
            return "nextdoor"

        # Check subject patterns
        if any(keyword in subject_lower for keyword in ["craigslist", "cl:"]):
            return "craigslist"
        if any(keyword in subject_lower for keyword in ["facebook", "marketplace"]):
            return "facebook"
        if any(keyword in subject_lower for keyword in ["offerup"]):
            return "offerup"

        return None

    async def _parse_platform_message(
        self,
        platform: str,
        sender: str,
        subject: str,
        body: str,
        email_message,
    ) -> IncomingMessageCreate | None:
        """Parse email into structured message data"""
        try:
            parsing_rules = self.default_parsing_rules.get(platform, {})
            extractors = parsing_rules.get("message_extractors", {})

            # Initialize message data
            # Build typed constructor args for IncomingMessageCreate to satisfy mypy
            message_text = body[:1000]
            raw_headers: dict[str, Any] = dict(email_message.items())
            message_data = {
                "platform": str(platform),
                "subject": str(subject),
                "message_text": str(message_text),
                "source_type": "email",
                "raw_data": {
                    "sender": str(sender),
                    "subject": str(subject),
                    "body": str(body),
                    "headers": raw_headers,
                },
            }

            # Extract sender information
            if "sender_email" in extractors:
                email_match = re.search(extractors["sender_email"], body, re.IGNORECASE)
                if email_match:
                    message_data["sender_email"] = email_match.group(1).strip()

            if "sender_name" in extractors:
                name_match = re.search(extractors["sender_name"], body, re.IGNORECASE)
                if name_match:
                    message_data["sender_name"] = name_match.group(1).strip()

            # Extract message content
            if "original_message" in extractors:
                msg_match = re.search(
                    extractors["original_message"],
                    body,
                    re.DOTALL | re.IGNORECASE,
                )
                if msg_match:
                    message_data["message_text"] = msg_match.group(1).strip()

            # Determine message type and priority
            message_type = self._classify_message_type(subject, body)
            priority = self._determine_priority(subject, body)

            # Ensure we pass correct types into IncomingMessageCreate
            platform_arg = str(message_data.get("platform", ""))
            subject_arg = str(message_data.get("subject", ""))
            message_text_arg = str(message_data.get("message_text", ""))
            sender_email_arg = (
                str(message_data.get("sender_email"))
                if message_data.get("sender_email") is not None
                else None
            )
            sender_name_arg = (
                str(message_data.get("sender_name"))
                if message_data.get("sender_name") is not None
                else None
            )
            raw_data_candidate = message_data.get("raw_data")
            if isinstance(raw_data_candidate, dict):
                raw_data_arg: dict[str, Any] = raw_data_candidate
            else:
                raw_data_arg = {}

            return IncomingMessageCreate(
                platform=platform_arg,
                subject=subject_arg,
                message_text=message_text_arg,
                message_type=message_type,
                priority=priority,
                sender_email=sender_email_arg,
                sender_name=sender_name_arg,
                raw_data=raw_data_arg,
            )

        except Exception as e:
            logger.error(f"Error parsing {platform} message: {e}")
            return None

    def _classify_message_type(self, subject: str, body: str) -> str:
        """Classify the type of message"""
        subject_lower = subject.lower()
        body_lower = body.lower()

        # Look for keywords to classify message
        if any(
            keyword in subject_lower + body_lower for keyword in self.PRICE_KEYWORDS
        ):
            return "price_inquiry"
        if any(
            keyword in subject_lower + body_lower
            for keyword in self.AVAILABILITY_KEYWORDS
        ):
            return "availability"
        if any(
            keyword in subject_lower + body_lower for keyword in self.MEETING_KEYWORDS
        ):
            return "meeting_request"
        if any(
            keyword in subject_lower + body_lower for keyword in self.INTEREST_KEYWORDS
        ):
            return "interest"
        return "inquiry"

    def _determine_priority(self, subject: str, body: str) -> str:
        """Determine message priority"""
        text = (subject + " " + body).lower()

        # High priority indicators
        if any(keyword in text for keyword in self.HIGH_PRIORITY_KEYWORDS):
            return "high"
        if any(keyword in text for keyword in self.NORMAL_PRIORITY_KEYWORDS):
            return "normal"
        return "low"

    async def _store_incoming_message(self, message: IncomingMessageCreate):
        """Store parsed message in database"""
        try:
            db = get_typed_db()

            # Convert to dict and add metadata
            message_data = message.dict()
            message_data["id"] = f"email_{uuid.uuid4().hex}_{message.platform}"
            message_data["user_id"] = "default"  # TODO: Support multi-tenant
            message_data["received_at"] = datetime.now().isoformat()

            # Generate content hash for duplicate detection
            content_hash = self._generate_content_hash(
                str(message.platform),
                str(message.sender_email or ""),
                str(message.message_text or ""),
            )
            message_data["content_hash"] = content_hash

            # Check for duplicates using content hash
            existing = await db.messages.find_one(
                {"user_id": message_data["user_id"], "content_hash": content_hash},
            )

            if not existing:
                # Insert into database
                await db.messages.insert_one(message_data)

                # Try to match with existing ad
                if message.sender_email or message.sender_name:
                    await self._match_message_to_ad(db, message_data)

                logger.info(f"Stored {message.platform} message from email")
            else:
                logger.info(f"Skipped duplicate {message.platform} message from email")

        except Exception as e:
            logger.error(f"Error storing message: {e}")

    async def _match_message_to_ad(self, db, message_data: dict):
        """Try to match incoming message to an existing ad"""
        try:
            # Search for ads that might match this inquiry
            # This is a simple implementation - could be enhanced with ML/NLP

            ads_cursor = db.ads.find(
                {
                    "user_id": message_data["user_id"],
                    "status": {"$in": ["posted", "active"]},
                    "platforms": message_data["platform"],
                },
            )

            ads = await ads_cursor.to_list(100)

            # Simple keyword matching
            message_text = message_data.get("message_text", "").lower()
            subject = message_data.get("subject", "").lower()

            for ad in ads:
                ad_title = ad.get("title", "").lower()
                ad_description = ad.get("description", "").lower()

                # Check if ad title/description keywords appear in message
                ad_words = set(ad_title.split() + ad_description.split())
                message_words = set(message_text.split() + subject.split())

                # If 2+ common words, consider it a match
                if len(ad_words.intersection(message_words)) >= 2:
                    await db.messages.update_one(
                        {"id": message_data["id"]},
                        {"$set": {"ad_id": ad["id"]}},
                    )
                    logger.info(f"Matched message to ad: {ad['title']}")
                    break

        except Exception as e:
            logger.error(f"Error matching message to ad: {e}")


# Email configuration management
class EmailConfigManager:
    """Manage email monitoring configurations"""

    @staticmethod
    async def setup_default_rules():
        """Setup default email parsing rules for common platforms"""
        db = get_typed_db()

        # Default rules for each platform
        default_rules = [
            EmailRule(
                platform="craigslist",
                sender_pattern="*@craigslist.org",
                subject_patterns=[
                    "Reply to your * ad",
                    "New reply to your ad",
                    "CL: * - *",
                ],
                parsing_rules={
                    "sender_email_pattern": r"From: (.+@.+)",
                    "message_pattern": r"Reply:\s*(.+?)(?:\n\n|$)",
                    "ad_title_pattern": r"Reply to your (.+) ad",
                },
            ),
            EmailRule(
                platform="facebook",
                sender_pattern="*@facebookmail.com",
                subject_patterns=[
                    "* sent you a message about *",
                    "New message about your listing",
                ],
                parsing_rules={
                    "sender_name_pattern": r"(.+) sent you a message",
                    "ad_title_pattern": r"message about (.+)",
                    "message_pattern": r"Message:\s*(.+?)(?:\n|$)",
                },
            ),
            EmailRule(
                platform="offerup",
                sender_pattern="*@offerup.com",
                subject_patterns=["* sent you a message", "New message from *"],
                parsing_rules={
                    "sender_name_pattern": r"(.+) sent you a message",
                    "message_pattern": r"Message:\s*(.+?)(?:\n|View|Reply)",
                },
            ),
        ]

        # Store rules in database
        for rule in default_rules:
            rule_data = rule.dict()
            rule_data["user_id"] = "default"

            # Check if rule already exists
            existing = await db.email_rules.find_one(
                {"user_id": rule_data["user_id"], "platform": rule_data["platform"]},
            )

            if not existing:
                await db.email_rules.insert_one(rule_data)
                logger.info(f"Created default email rule for {rule.platform}")


# Global email monitoring service instance
email_monitoring_service = None
email_monitoring_task = None


async def start_email_monitoring(email_config: dict):
    """Start the global email monitoring service"""
    global email_monitoring_service, email_monitoring_task

    if email_monitoring_service is None:
        email_monitoring_service = EmailMonitoringService(email_config)

        # Setup default rules
        await EmailConfigManager.setup_default_rules()

        # Start monitoring in background task if not already running
        if email_monitoring_task is None or email_monitoring_task.done():
            email_monitoring_task = asyncio.create_task(
                email_monitoring_service.start_monitoring(),
            )

        logger.info("Email monitoring service started")


async def stop_email_monitoring():
    """Stop the global email monitoring service"""
    global email_monitoring_service, email_monitoring_task

    if email_monitoring_service:
        email_monitoring_service.stop_monitoring()
        email_monitoring_service = None

    if email_monitoring_task and not email_monitoring_task.done():
        try:
            email_monitoring_task.cancel()
            await email_monitoring_task
        except asyncio.CancelledError:
            pass
        email_monitoring_task = None

    logger.info("Email monitoring service stopped")
