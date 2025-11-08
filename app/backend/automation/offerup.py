"""OfferUp automation
Handles posting ads to OfferUp marketplace
"""

import time

from .base import (
    AdData,
    PlatformAutomationBase,
    PlatformCredentials,
    PostResult,
    PostStatus,
)


class OfferUpAutomation(PlatformAutomationBase):
    """OfferUp posting automation"""

    def __init__(self, headless: bool = True):
        super().__init__("offerup", headless, rate_limit=0.3)  # 0.3 requests per second

        self.base_url = "https://offerup.com"
        self.login_url = "https://offerup.com/login"
        self.post_url = "https://offerup.com/sell"

        # Category mapping for OfferUp
        self.category_mapping = {
            "electronics": "electronics",
            "furniture": "home-garden",
            "vehicles": "auto-parts",
            "real estate": "housing",
            "appliances": "home-garden",
            "clothing": "clothing-shoes",
            "sports": "sporting-goods",
            "tools": "home-garden",
            "other": "everything-else",
        }

    async def login(self, credentials: PlatformCredentials) -> bool:
        """Login to OfferUp"""
        try:
            self.logger.info("Navigating to OfferUp login")
            page = self._ensure_page()
            await page.goto(self.login_url)
            await self.random_delay(2, 4)

            # Wait for login form
            try:
                await page.wait_for_selector(
                    '[data-testid="email-input"]',
                    timeout=10000,
                )
            except Exception:
                # Try alternative selectors
                await page.wait_for_selector('input[type="email"]', timeout=10000)

            # Fill email
            email_selectors = [
                '[data-testid="email-input"]',
                'input[type="email"]',
                'input[name="email"]',
                "#email",
            ]

            email_filled = False
            for selector in email_selectors:
                if await page.locator(selector).is_visible(timeout=2000):
                    if await self.safe_fill(selector, credentials.username):
                        email_filled = True
                        break

            if not email_filled:
                return False

            # Fill password
            password_selectors = [
                '[data-testid="password-input"]',
                'input[type="password"]',
                'input[name="password"]',
                "#password",
            ]

            password_filled = False
            for selector in password_selectors:
                if await page.locator(selector).is_visible(timeout=2000):
                    if await self.safe_fill(selector, credentials.password):
                        password_filled = True
                        break

            if not password_filled:
                return False

            # Click login button
            login_selectors = [
                '[data-testid="login-button"]',
                'button[type="submit"]',
                'input[type="submit"]',
                'button:has-text("Log in")',
                'button:has-text("Sign in")',
            ]

            login_clicked = False
            for selector in login_selectors:
                if await page.locator(selector).is_visible(timeout=2000):
                    if await self.safe_click(selector):
                        login_clicked = True
                        break

            if not login_clicked:
                return False

            await self.random_delay(3, 5)

            # Verify login success
            return await self._verify_login()

        except Exception as e:
            self.logger.error(f"Login failed: {e}")
            return False

    async def _verify_login(self) -> bool:
        """Verify successful login to OfferUp"""
        try:
            # Look for indicators of successful login
            success_indicators = [
                '[data-testid="user-menu"]',
                '[data-testid="profile-menu"]',
                'a[href="/profile"]',
                'button:has-text("Sell")',
                ".user-avatar",
                '[data-testid="sell-button"]',
            ]

            page = self._ensure_page()
            for selector in success_indicators:
                if await page.locator(selector).is_visible(timeout=5000):
                    self.logger.info("OfferUp login verified")
                    return True

            # Check if we're still on login page (login failed)
            if "login" in page.url.lower():
                self.logger.error("Still on login page - login failed")
                return False

            # If we're on a different page, assume login was successful
            self.logger.info("Login appears successful")
            return True

        except Exception as e:
            self.logger.error(f"Error verifying login: {e}")
            return False

    async def post_ad(
        self,
        ad_data: AdData,
        credentials: PlatformCredentials,
    ) -> PostResult:
        """Post ad to OfferUp"""
        try:
            # Login first
            if not await self.login(credentials):
                return PostResult(
                    status=PostStatus.LOGIN_REQUIRED,
                    message="Failed to login to OfferUp",
                )

            # Navigate to sell page
            self.logger.info("Navigating to OfferUp sell page")
            page = self._ensure_page()
            await page.goto(self.post_url)
            await self.random_delay(2, 4)

            # Handle CAPTCHA if present
            if not await self.wait_and_handle_captcha():
                return PostResult(
                    status=PostStatus.CAPTCHA_REQUIRED,
                    message="CAPTCHA required",
                )

            # Fill listing form
            return await self._fill_listing_form(ad_data)

        except Exception as e:
            self.logger.error(f"Error posting ad: {e}")
            return PostResult(status=PostStatus.FAILED, message=str(e))

    async def _fill_listing_form(self, ad_data: AdData) -> PostResult:
        """Fill the OfferUp listing form"""
        try:
            # Wait for form to load
            page = self._ensure_page()
            await page.wait_for_selector(
                '[data-testid="sell-form"], .sell-form, #sell-form',
                timeout=15000,
            )
            await self.random_delay(1, 2)

            # Fill title
            title_selectors = [
                '[data-testid="title-input"]',
                'input[name="title"]',
                'input[placeholder*="title"]',
                ".title-input input",
            ]

            title_filled = False
            for selector in title_selectors:
                if await page.locator(selector).is_visible(timeout=3000):
                    if await self.safe_fill(selector, ad_data.title):
                        title_filled = True
                        break

            if not title_filled:
                return PostResult(
                    status=PostStatus.FAILED,
                    message="Failed to fill title",
                )

            # Select category
            await self._select_category(ad_data.category)

            # Fill price
            price_selectors = [
                '[data-testid="price-input"]',
                'input[name="price"]',
                'input[type="number"]',
                'input[placeholder*="price"]',
            ]

            price_filled = False
            for selector in price_selectors:
                if await page.locator(selector).is_visible(timeout=3000):
                    if await self.safe_fill(selector, str(int(ad_data.price))):
                        price_filled = True
                        break

            if not price_filled:
                return PostResult(
                    status=PostStatus.FAILED,
                    message="Failed to fill price",
                )

            # Fill description
            description_selectors = [
                '[data-testid="description-input"]',
                'textarea[name="description"]',
                'textarea[placeholder*="description"]',
                ".description-input textarea",
            ]

            description_filled = False
            for selector in description_selectors:
                if await page.locator(selector).is_visible(timeout=3000):
                    if await self.safe_fill(selector, ad_data.description):
                        description_filled = True
                        break

            if not description_filled:
                return PostResult(
                    status=PostStatus.FAILED,
                    message="Failed to fill description",
                )

            # Handle location
            await self._set_location(ad_data.location)

            # Upload images if provided
            if ad_data.images:
                await self._upload_images(ad_data.images)

            # Submit the listing
            return await self._submit_listing()

        except Exception as e:
            self.logger.error(f"Error filling form: {e}")
            return PostResult(status=PostStatus.FAILED, message=str(e))

    async def _select_category(self, category: str) -> bool:
        """Select category for OfferUp listing"""
        try:
            category_mapped = self.category_mapping.get(
                category.lower(),
                "everything-else",
            )

            # Look for category selector/dropdown
            category_selectors = [
                '[data-testid="category-select"]',
                'select[name="category"]',
                ".category-select",
                '[data-testid="category-dropdown"]',
            ]

            page = self._ensure_page()
            for selector in category_selectors:
                if await page.locator(selector).is_visible(timeout=3000):
                    # Try to select the category
                    try:
                        await page.select_option(selector, value=category_mapped)
                        await self.random_delay(0.5, 1.0)
                        return True
                    except Exception:
                        # Try clicking approach
                        await self.safe_click(selector)
                        await self.random_delay(0.5, 1.0)

                        # Look for category option
                        category_option = f'[data-value="{category_mapped}"], [value="{category_mapped}"]'
                        if await page.locator(category_option).is_visible(
                            timeout=3000,
                        ):
                            await self.safe_click(category_option)
                            return True

            # If no category selector found, continue anyway
            self.logger.warning("Could not find category selector")
            return True

        except Exception as e:
            self.logger.error(f"Error selecting category: {e}")
            return False

    async def _set_location(self, location: str) -> bool:
        """Set location for OfferUp listing"""
        try:
            location_selectors = [
                '[data-testid="location-input"]',
                'input[name="location"]',
                'input[placeholder*="location"]',
                ".location-input input",
            ]

            page = self._ensure_page()
            for selector in location_selectors:
                if await page.locator(selector).is_visible(timeout=3000):
                    await self.safe_fill(selector, location)
                    await self.random_delay(1, 2)

                    # Handle location suggestions dropdown
                    suggestion_selectors = [
                        ".location-suggestion:first-child",
                        '[data-testid="location-suggestion"]:first-child',
                        ".suggestion-item:first-child",
                    ]

                    for suggestion_selector in suggestion_selectors:
                        if await page.locator(suggestion_selector).is_visible(
                            timeout=3000,
                        ):
                            await self.safe_click(suggestion_selector)
                            return True

                    return True

            return True  # Continue even if location field not found

        except Exception as e:
            self.logger.error(f"Error setting location: {e}")
            return False

    async def _upload_images(self, image_urls: list[str]) -> bool:
        """Upload images to OfferUp listing"""
        try:
            # Look for image upload area
            upload_selectors = [
                '[data-testid="image-upload"]',
                'input[type="file"]',
                ".image-upload input",
                '[data-testid="photo-upload"]',
            ]

            page = self._ensure_page()
            for selector in upload_selectors:
                if await page.locator(selector).is_visible(timeout=3000):
                    self.logger.info(
                        f"Image upload found - {len(image_urls)} images provided",
                    )
                    # TODO: Implement actual image download and upload
                    return True

            return False

        except Exception as e:
            self.logger.error(f"Image upload failed: {e}")
            return False

    async def _submit_listing(self) -> PostResult:
        """Submit the OfferUp listing"""
        try:
            # Look for submit/post button
            submit_selectors = [
                '[data-testid="submit-button"]',
                '[data-testid="post-button"]',
                'button[type="submit"]',
                'button:has-text("Post")',
                'button:has-text("List item")',
                'button:has-text("Publish")',
                ".post-button",
                ".submit-button",
            ]

            submit_clicked = False
            page = self._ensure_page()
            for selector in submit_selectors:
                if await page.locator(selector).is_visible(timeout=5000):
                    if await self.safe_click(selector):
                        submit_clicked = True
                        break

            if not submit_clicked:
                return PostResult(
                    status=PostStatus.FAILED,
                    message="Could not find submit button",
                )

            await self.random_delay(3, 6)

            # Check for success indicators
            success_indicators = [
                'text="Your item is now live"',
                'text="Successfully posted"',
                'text="Item posted"',
                '[data-testid="success-message"]',
                ".success-message",
                'text="listed successfully"',
            ]

            for selector in success_indicators:
                if await page.locator(selector).is_visible(timeout=10000):
                    listing_url = await self._extract_listing_url()

                    return PostResult(
                        status=PostStatus.SUCCESS,
                        post_url=listing_url,
                        platform_ad_id=self._generate_offerup_id(),
                        message="Successfully posted to OfferUp",
                    )

            # Check for errors
            error_messages = await self._check_for_errors()
            if error_messages:
                return PostResult(
                    status=PostStatus.FAILED,
                    message=f"OfferUp errors: {', '.join(error_messages)}",
                )

            return PostResult(
                status=PostStatus.FAILED,
                message="Posting status unknown",
            )

        except Exception as e:
            self.logger.error(f"Error submitting listing: {e}")
            return PostResult(status=PostStatus.FAILED, message=str(e))

    async def _extract_listing_url(self) -> str | None:
        """Extract the URL of the created listing"""
        try:
            page = self._ensure_page()
            current_url = page.url

            # OfferUp listing URLs typically include /item/
            if "/item/" in current_url:
                return current_url

            # Look for links to the listing
            link_selectors = [
                'a[href*="/item/"]',
                '[data-testid="listing-link"]',
                'a:has-text("View your item")',
            ]

            page = self._ensure_page()
            for selector in link_selectors:
                if await page.locator(selector).is_visible(timeout=5000):
                    href = await page.locator(selector).get_attribute("href")
                    if href:
                        if href.startswith("/"):
                            return f"{self.base_url}{href}"
                        return href

            return None

        except Exception as e:
            self.logger.error(f"Error extracting listing URL: {e}")
            return None

    def _generate_offerup_id(self) -> str:
        """Generate an OfferUp-style listing ID"""
        return f"ou_{int(time.time())}"

    async def _check_for_errors(self) -> list[str]:
        """Check for OfferUp-specific error messages"""
        error_messages = []

        try:
            error_selectors = [
                ".error-message",
                '[data-testid="error-message"]',
                ".alert-error",
                'text="error"',
                'text="failed"',
                ".validation-error",
            ]

            page = self._ensure_page()
            for selector in error_selectors:
                elements = await page.locator(selector).all()
                for element in elements:
                    if await element.is_visible():
                        text = await element.text_content()
                        if text and text.strip():
                            error_messages.append(text.strip())

        except Exception as e:
            self.logger.error(f"Error checking for errors: {e}")

        return error_messages

    async def validate_credentials(self, credentials: PlatformCredentials) -> bool:
        """Validate OfferUp credentials"""
        try:
            return await self.login(credentials)
        except Exception as e:
            self.logger.error(f"Credential validation failed: {e}")
            return False

    def get_supported_categories(self) -> list[str]:
        """Get supported OfferUp categories"""
        return list(self.category_mapping.keys())
