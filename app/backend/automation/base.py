"""Base class for all platform automations
Provides common functionality for web scraping, session management, and error handling
"""

import asyncio
import logging
import random
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional, cast

from asyncio_throttle import Throttler
from fake_useragent import UserAgent
from playwright.async_api import Browser, BrowserContext, Page, async_playwright


class PageNotInitializedError(RuntimeError):
    """Raised when attempting to use page before browser initialization"""

    def __init__(self, message: str = "Page not initialized. Call initialize() first."):
        super().__init__(message)
        self.message = message


class PostStatus(Enum):
    SUCCESS = "success"
    FAILED = "failed"
    RATE_LIMITED = "rate_limited"
    ACCOUNT_BLOCKED = "account_blocked"
    CAPTCHA_REQUIRED = "captcha_required"
    LOGIN_REQUIRED = "login_required"


@dataclass
class PostResult:
    status: PostStatus
    platform_ad_id: str | None = None
    post_url: str | None = None
    message: str | None = None
    error_code: str | None = None
    retry_after: int | None = None  # seconds

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["status"] = self.status.value
        return result


@dataclass
class AdData:
    title: str
    description: str
    price: float
    category: str
    location: str
    images: list[str]
    contact_info: dict[str, str] | None = None
    additional_data: dict[str, Any] | None = None


@dataclass
class PlatformCredentials:
    username: str
    password: str
    email: str | None = None
    phone: str | None = None
    additional_data: dict[str, str] | None = None


class PlatformAutomationBase(ABC):
    """Abstract base class for platform automations"""

    def __init__(
        self,
        platform_name: str,
        headless: bool = True,
        rate_limit: float = 1.0,
    ):
        self.platform_name = platform_name
        self.headless = headless
        self.rate_limit = rate_limit  # requests per second
        # Throttler expects an int rate_limit; coerce floats safely
        self.throttler = Throttler(rate_limit=int(rate_limit))

        # Session management
        self.browser: Browser | None = None
        self.context: BrowserContext | None = None
        self.page: Page | None = None

        # Configuration
        self.user_agent = UserAgent()
        # Ensure logger name uses instance attribute if available
        self.logger = logging.getLogger(f"automation.{self.platform_name}")

        # Error tracking
        self.consecutive_failures: int = 0
        # Timestamp of last success or None
        self.last_success_time: Optional[datetime] = None
        # When rate-limited until, or None
        self.blocked_until: Optional[datetime] = None

    def _ensure_page(self) -> Page:
        """Ensure page is initialized and return it. Raises PageNotInitializedError if not."""
        if not self.page:
            raise PageNotInitializedError
        return self.page

    async def goto(self, url: str, **kwargs) -> None:
        """Navigate to a URL"""
        page = self._ensure_page()
        await page.goto(url, **kwargs)

    async def wait_for_selector(self, selector: str, **kwargs):
        """Wait for a selector"""
        page = self._ensure_page()
        return await page.wait_for_selector(selector, **kwargs)

    def locator(self, selector: str):
        """Get a locator (synchronous method)"""
        page = self._ensure_page()
        return page.locator(selector)

    async def wait_for_load_state(
        self,
        # Use a plain str here to avoid relying on Literal availability in all
        # linting/runtime environments. Callers should pass one of the
        # Playwright-supported states: "domcontentloaded", "load", "networkidle".
        state: str = "load",
        **kwargs,
    ):
        """Wait for load state"""
        page = self._ensure_page()
        # Playwright expects a Literal for states; pass the runtime string value
        # directly — this keeps the runtime behavior identical while avoiding
        # import/use of Literal in other files that previously triggered linter
        # errors in this repo's toolchain.
        # Cast state to the narrower Literal union that Playwright expects.
        await page.wait_for_load_state(cast(Any, state), **kwargs)

    @property
    def url(self) -> str:
        """Get current page URL"""
        page = self._ensure_page()
        return page.url

    async def select_option(self, selector: str, **kwargs):
        """Select an option from a select element"""
        page = self._ensure_page()
        return await page.select_option(selector, **kwargs)

    async def set_input_files(self, selector: str, files):
        """Set input files for file upload"""
        locator = self.locator(selector)
        await locator.set_input_files(files)

    async def count(self, selector: str) -> int:
        """Count elements matching selector"""
        locator = self.locator(selector)
        count = await locator.count()
        return int(count) if count is not None else 0

    async def all_elements(self, selector: str):
        """Get all elements matching selector"""
        locator = self.locator(selector)
        return await locator.all()

    async def __aenter__(self):
        """Async context manager entry"""
        await self.initialize_browser()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.cleanup()

    async def initialize_browser(self) -> None:
        """Initialize Playwright browser and context"""
        try:
            self.playwright = await async_playwright().start()

            # Launch browser with stealth settings
            self.browser = await self.playwright.chromium.launch(
                headless=self.headless,
                args=[
                    "--no-sandbox",
                    "--disable-blink-features=AutomationControlled",
                    "--disable-web-security",
                    "--disable-dev-shm-usage",
                    "--disable-background-timer-throttling",
                    "--disable-backgrounding-occluded-windows",
                    "--disable-renderer-backgrounding",
                ],
            )

            # Create context with random user agent
            self.context = await self.browser.new_context(
                user_agent=self.user_agent.random,
                viewport={"width": 1920, "height": 1080},
                locale="en-US",
                timezone_id="America/New_York",
                extra_http_headers={
                    "Accept-Language": "en-US,en;q=0.9",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                    "Connection": "keep-alive",
                    "Upgrade-Insecure-Requests": "1",
                },
            )

            # Create page
            self.page = await self.context.new_page()

            # Add stealth scripts
            await self.page.add_init_script(
                """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                });

                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5],
                });

                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en'],
                });
            """,
            )

            self.logger.info(f"Browser initialized for {self.platform_name}")

        except Exception as e:
            self.logger.error(f"Failed to initialize browser: {e}")
            raise

    async def cleanup(self) -> None:
        """Clean up browser resources"""
        try:
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if hasattr(self, "playwright"):
                await self.playwright.stop()

            self.logger.info(f"Browser cleanup completed for {self.platform_name}")

        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")

    async def random_delay(
        self,
        min_seconds: float = 1.0,
        max_seconds: float = 3.0,
    ) -> None:
        """Add random delay to mimic human behavior"""
        delay = random.uniform(min_seconds, max_seconds)
        await asyncio.sleep(delay)

    async def safe_click(self, selector: str, timeout: int = 30000) -> bool:
        """Safely click an element with retries"""
        try:
            page = self._ensure_page()
            await page.wait_for_selector(selector, timeout=timeout)
            await self.random_delay(0.5, 1.5)
            await page.click(selector)
            await self.random_delay(1.0, 2.0)
            return True
        except Exception as e:
            self.logger.error(f"Failed to click {selector}: {e}")
            return False

    async def safe_fill(self, selector: str, text: str, timeout: int = 30000) -> bool:
        """Safely fill an input field"""
        try:
            page = self._ensure_page()
            await page.wait_for_selector(selector, timeout=timeout)
            await self.random_delay(0.5, 1.5)

            # Clear existing text
            await page.fill(selector, "")
            await self.random_delay(0.3, 0.8)

            # Type with human-like speed
            await page.type(selector, text, delay=random.randint(50, 150))
            await self.random_delay(0.5, 1.0)
            return True
        except Exception as e:
            self.logger.error(f"Failed to fill {selector}: {e}")
            return False

    async def wait_and_handle_captcha(self, timeout: int = 60000) -> bool:
        """Wait for and handle CAPTCHA if present"""
        try:
            page = self._ensure_page()
            # This is a placeholder - in production you'd integrate with CAPTCHA solving services

            # Check for common CAPTCHA indicators
            captcha_selectors = [
                '[data-testid="captcha"]',
                ".g-recaptcha",
                "#captcha",
                'iframe[src*="captcha"]',
                'iframe[src*="recaptcha"]',
            ]

            for selector in captcha_selectors:
                if await page.locator(selector).is_visible():
                    self.logger.warning(
                        "CAPTCHA detected - manual intervention required",
                    )
                    return False

            return True

        except Exception as e:
            self.logger.error(f"Error checking for CAPTCHA: {e}")
            return False

    def is_rate_limited(self) -> bool:
        """Check if we're currently rate limited"""
        if self.blocked_until and datetime.now() < self.blocked_until:
            return True
        return False

    def mark_rate_limited(self, retry_after: int = 300) -> None:
        """Mark the automation as rate limited"""
        self.blocked_until = datetime.now() + timedelta(seconds=retry_after)
        self.consecutive_failures += 1
        self.logger.warning(f"Rate limited for {retry_after} seconds")

    def mark_success(self) -> None:
        """Mark a successful operation"""
        self.consecutive_failures = 0
        self.last_success_time = datetime.now()
        self.blocked_until = None

    @abstractmethod
    async def login(self, credentials: "PlatformCredentials") -> bool:
        """Login to the platform"""

    @abstractmethod
    async def post_ad(
        self,
        ad_data: "AdData",
        credentials: "PlatformCredentials",
    ) -> "PostResult":
        """Post an ad to the platform"""

    @abstractmethod
    async def validate_credentials(self, credentials: "PlatformCredentials") -> bool:
        """Validate platform credentials"""

    @abstractmethod
    def get_supported_categories(self) -> list[str]:
        """Get list of supported categories for this platform"""


class AutomationManager:
    """Manages multiple platform automations"""

    def __init__(self):
        self.platforms: dict[str, PlatformAutomationBase] = {}
        self.logger = logging.getLogger("automation.manager")

    def register_platform(self, platform: PlatformAutomationBase) -> None:
        """Register a platform automation"""
        self.platforms[platform.platform_name] = platform
        self.logger.info(f"Registered platform: {platform.platform_name}")

    async def post_to_platform(
        self,
        platform_name: str,
        ad_data: AdData,
        credentials: PlatformCredentials,
    ) -> PostResult:
        """Post ad to specific platform"""
        if platform_name not in self.platforms:
            return PostResult(
                status=PostStatus.FAILED,
                message=f"Platform {platform_name} not supported",
            )

        platform = self.platforms[platform_name]

        # Check rate limiting
        if platform.is_rate_limited():
            return PostResult(
                status=PostStatus.RATE_LIMITED,
                message="Platform is rate limited",
                retry_after=int(
                    (platform.blocked_until - datetime.now()).total_seconds()
                    if platform.blocked_until
                    else 0
                ),
            )

        try:
            async with platform:
                # Validate credentials
                if not await platform.validate_credentials(credentials):
                    return PostResult(
                        status=PostStatus.LOGIN_REQUIRED,
                        message="Invalid credentials",
                    )

                # Attempt to post
                result = await platform.post_ad(ad_data, credentials)

                if result.status == PostStatus.SUCCESS:
                    platform.mark_success()
                elif result.status == PostStatus.RATE_LIMITED:
                    platform.mark_rate_limited(result.retry_after or 300)

                return result

        except Exception as e:
            platform.consecutive_failures += 1
            self.logger.error(f"Error posting to {platform_name}: {e}")

            return PostResult(
                status=PostStatus.FAILED,
                message=str(e),
                error_code="AUTOMATION_ERROR",
            )

    async def post_to_multiple_platforms(
        self,
        platforms: list[str],
        ad_data: AdData,
        credentials_map: dict[str, PlatformCredentials],
    ) -> dict[str, PostResult]:
        """Post ad to multiple platforms concurrently"""
        tasks = []
        for platform_name in platforms:
            if platform_name in credentials_map:
                task = self.post_to_platform(
                    platform_name,
                    ad_data,
                    credentials_map[platform_name],
                )
                tasks.append((platform_name, task))

        results = {}
        for platform_name, task in tasks:
            try:
                results[platform_name] = await task
            except Exception as e:
                results[platform_name] = PostResult(
                    status=PostStatus.FAILED,
                    message=str(e),
                )

        return results


# Global automation manager instance
automation_manager = AutomationManager()
