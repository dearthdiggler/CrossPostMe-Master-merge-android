"""Facebook Marketplace automation
Handles posting ads to Facebook Marketplace with authentication and error handling
"""

import asyncio
import os
import tempfile
import time

import aiofiles
import httpx

from .base import (
    AdData,
    PlatformAutomationBase,
    PlatformCredentials,
    PostResult,
    PostStatus,
)


class FacebookMarketplaceAutomation(PlatformAutomationBase):
    """Facebook Marketplace posting automation"""

    def __init__(self, headless: bool = True):
        super().__init__(
            "facebook",
            headless,
            rate_limit=0.5,
        )  # 0.5 requests per second

        self.base_url = "https://www.facebook.com"
        self.marketplace_url = "https://www.facebook.com/marketplace"
        self.create_url = "https://www.facebook.com/marketplace/create"

        # Configure timeout settings
        self._configure_timeouts()

        # Category mapping
        self.category_mapping = {
            "electronics": "ELECTRONICS",
            "furniture": "HOME_GARDEN",
            "vehicles": "VEHICLE",
            "real estate": "PROPERTY_RENTALS",
            "appliances": "HOME_GARDEN",
            "clothing": "APPAREL",
            "sports": "SPORTING_GOODS",
            "tools": "HOME_GARDEN",
            "other": "OTHER",
        }

    def _configure_timeouts(self) -> None:
        """Configure timeout settings from environment or use sensible defaults"""
        # Default timeout values (in seconds)
        self.default_download_timeout = (
            120  # Increased from 30s to 120s for large images
        )
        self.default_upload_timeout = 120  # Upload completion timeout

        # Read from environment variables with validation and fallbacks
        try:
            download_timeout = os.environ.get(
                "FACEBOOK_DOWNLOAD_TIMEOUT",
                str(self.default_download_timeout),
            )
            self.download_timeout = max(30, int(download_timeout))  # Minimum 30s
        except (ValueError, TypeError):
            self.logger.warning("Invalid FACEBOOK_DOWNLOAD_TIMEOUT, using default")
            self.download_timeout = self.default_download_timeout

        try:
            upload_timeout = os.environ.get(
                "FACEBOOK_UPLOAD_TIMEOUT",
                str(self.default_upload_timeout),
            )
            self.upload_timeout = max(60, int(upload_timeout))  # Minimum 60s
        except (ValueError, TypeError):
            self.logger.warning("Invalid FACEBOOK_UPLOAD_TIMEOUT, using default")
            self.upload_timeout = self.default_upload_timeout

        self.logger.info(
            f"Facebook automation timeouts: download={self.download_timeout}s, upload={self.upload_timeout}s",
        )

    async def login(self, credentials: PlatformCredentials) -> bool:
        """Login to Facebook"""
        try:
            self.logger.info("Navigating to Facebook login")
            page = self._ensure_page()
            await page.goto(self.base_url)
            await self.random_delay(2, 4)

            # Handle cookie consent if present
            try:
                await page.click(
                    '[data-testid="cookie-policy-manage-dialog-accept-button"]',
                    timeout=5000,
                )
                await self.random_delay(1, 2)
            except Exception:
                pass  # No cookie dialog

            # Check if already logged in
            try:
                await page.wait_for_selector(
                    '[data-testid="royal_login_form"]',
                    timeout=3000,
                )
            except Exception:
                # Already logged in, check for marketplace access
                await page.goto(self.marketplace_url)
                return await self._verify_marketplace_access()

            # Fill login form
            self.logger.info("Filling login credentials")

            # Email field
            email_selector = "#email"
            if not await self.safe_fill(email_selector, credentials.username):
                return False

            # Password field
            password_selector = "#pass"
            if not await self.safe_fill(password_selector, credentials.password):
                return False

            # Click login button
            login_button = '[data-testid="royal_login_button"]'
            if not await self.safe_click(login_button):
                return False

            await self.random_delay(3, 5)

            # Handle two-factor authentication if required
            if await self._handle_2fa():
                await self.random_delay(2, 4)

            # Check for login success
            await page.goto(self.marketplace_url)
            return await self._verify_marketplace_access()

        except Exception as e:
            self.logger.error(f"Login failed: {e}")
            return False

    async def _handle_2fa(self) -> bool:
        """Handle two-factor authentication"""
        try:
            # Check for 2FA prompt
            page = self._ensure_page()
            if await page.locator('[data-testid="checkpoint_title"]').is_visible(
                timeout=5000,
            ):
                self.logger.warning("2FA required - manual intervention needed")
                # In production, you'd integrate with SMS services or authenticator apps
                return False
            return True
        except Exception:
            return True

    async def _verify_marketplace_access(self) -> bool:
        """Verify we have access to Facebook Marketplace"""
        try:
            # Look for marketplace-specific elements
            marketplace_indicators = [
                '[data-testid="marketplace_tab"]',
                'a[href="/marketplace"]',
                '[aria-label="Marketplace"]',
            ]

            page = self._ensure_page()
            for selector in marketplace_indicators:
                if await page.locator(selector).is_visible(timeout=5000):
                    self.logger.info("Marketplace access verified")
                    return True

            self.logger.error("No marketplace access detected")
            return False

        except Exception as e:
            self.logger.error(f"Error verifying marketplace access: {e}")
            return False

    async def post_ad(
        self,
        ad_data: AdData,
        credentials: PlatformCredentials,
    ) -> PostResult:
        """Post ad to Facebook Marketplace"""
        try:
            # Login first
            if not await self.login(credentials):
                return PostResult(
                    status=PostStatus.LOGIN_REQUIRED,
                    message="Failed to login to Facebook",
                )

            # Navigate to create listing page
            self.logger.info("Navigating to create listing")
            page = self._ensure_page()
            await page.goto(self.create_url)
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
        """Fill the Facebook Marketplace listing form"""
        try:
            # Wait for form to load
            page = self._ensure_page()
            await page.wait_for_selector(
                '[data-testid="marketplace-composer-form"]',
                timeout=10000,
            )

            # Select category
            category = self.category_mapping.get(ad_data.category.lower(), "OTHER")
            category_selector = f'[data-testid="marketplace-category-{category}"]'

            if await page.locator(category_selector).is_visible(timeout=5000):
                await self.safe_click(category_selector)
                await self.random_delay(1, 2)

            # Fill title
            title_selector = '[data-testid="marketplace-composer-title-input"]'
            if not await self.safe_fill(title_selector, ad_data.title):
                return PostResult(
                    status=PostStatus.FAILED,
                    message="Failed to fill title",
                )

            # Fill price
            price_selector = '[data-testid="marketplace-composer-price-input"]'
            if not await self.safe_fill(price_selector, str(int(ad_data.price))):
                return PostResult(
                    status=PostStatus.FAILED,
                    message="Failed to fill price",
                )

            # Fill description
            description_selector = (
                '[data-testid="marketplace-composer-description-input"]'
            )
            if not await self.safe_fill(description_selector, ad_data.description):
                return PostResult(
                    status=PostStatus.FAILED,
                    message="Failed to fill description",
                )

            # Fill location
            location_selector = '[data-testid="marketplace-composer-location-input"]'
            if not await self.safe_fill(location_selector, ad_data.location):
                return PostResult(
                    status=PostStatus.FAILED,
                    message="Failed to fill location",
                )

            # Upload images (if provided)
            if ad_data.images:
                await self._upload_images(ad_data.images)

            # Submit the listing
            submit_button = '[data-testid="marketplace-composer-publish-button"]'
            if not await self.safe_click(submit_button):
                return PostResult(
                    status=PostStatus.FAILED,
                    message="Failed to submit listing",
                )

            await self.random_delay(3, 5)

            # Wait for success confirmation
            success_indicators = [
                '[data-testid="marketplace-success-modal"]',
                'text="Your listing has been posted"',
                'text="Listing created"',
            ]

            for selector in success_indicators:
                if await page.locator(selector).is_visible(timeout=10000):
                    # Extract listing URL if possible
                    listing_url = await self._extract_listing_url()

                    return PostResult(
                        status=PostStatus.SUCCESS,
                        post_url=listing_url,
                        platform_ad_id=self._generate_facebook_id(),
                        message="Successfully posted to Facebook Marketplace",
                    )

            # Check for errors
            error_messages = await self._check_for_errors()
            if error_messages:
                return PostResult(
                    status=PostStatus.FAILED,
                    message=f"Facebook errors: {', '.join(error_messages)}",
                )

            return PostResult(
                status=PostStatus.FAILED,
                message="Unknown error - listing may not have been created",
            )

        except Exception as e:
            self.logger.error(f"Error filling form: {e}")
            return PostResult(status=PostStatus.FAILED, message=str(e))

    async def _upload_images(self, image_urls: list[str]) -> bool:
        """Upload images to Facebook Marketplace"""
        if not image_urls:
            return True

        temp_files = []
        try:
            # Step 1: Download images to temporary files
            self.logger.info(f"Downloading {len(image_urls)} images for upload")
            temp_files = await self._download_images(image_urls)

            if not temp_files:
                self.logger.warning("No images successfully downloaded")
                return False

            # Step 2: Wait for upload input and trigger file chooser
            upload_button = '[data-testid="marketplace-composer-photo-upload"]'
            file_input = 'input[type="file"][accept*="image"]'

            page = self._ensure_page()
            if await page.locator(upload_button).is_visible(timeout=5000):
                self.logger.info(
                    f"Found upload button, uploading {len(temp_files)} images",
                )

                # Try direct file input first
                try:
                    await page.set_input_files(file_input, temp_files)
                    self.logger.info("Used direct file input method")
                except Exception as direct_error:
                    self.logger.debug(
                        f"Direct file input failed: {direct_error}, trying file chooser",
                    )

                    # Fallback to file chooser method
                    async with page.expect_file_chooser() as fc_info:
                        await page.click(upload_button)
                    file_chooser = await fc_info.value
                    await file_chooser.set_files(temp_files)
                    self.logger.info("Used file chooser method")

                # Step 3: Wait for uploads to complete
                await self._wait_for_upload_completion(len(temp_files))
                return True
            self.logger.error("Upload button not found")
            return False

        except Exception as e:
            self.logger.error(f"Image upload failed: {e}")
            return False
        finally:
            # Step 4: Clean up temporary files
            await self._cleanup_temp_files(temp_files)

    async def _download_images(
        self,
        image_urls: list[str],
        max_retries: int = 3,
        timeout: int | None = None,
    ) -> list[str]:
        """Download images to temporary files with retry logic"""
        temp_files = []

        # Use configured timeout or provided override
        effective_timeout = timeout if timeout is not None else self.download_timeout

        # Validate timeout value
        if effective_timeout < 30:
            self.logger.warning(
                f"Timeout {effective_timeout}s is too low, using minimum 30s",
            )
            effective_timeout = 30

        self.logger.debug(f"Using download timeout: {effective_timeout}s")
        async with httpx.AsyncClient(timeout=effective_timeout) as client:
            for i, url in enumerate(image_urls):
                # Create temporary file once per image (outside retry loop)
                temp_dir = tempfile.gettempdir()
                file_extension = self._get_image_extension(url)
                temp_file = os.path.join(temp_dir, f"fb_upload_{i}{file_extension}")

                # Add to tracking list immediately for proper cleanup
                temp_files.append(temp_file)

                for attempt in range(max_retries):
                    try:
                        self.logger.debug(
                            f"Downloading {url} to {temp_file} (attempt {attempt + 1})",
                        )

                        # Download with exponential backoff
                        response = await client.get(url)
                        response.raise_for_status()

                        # Write to temporary file (overwrites on retry)
                        async with aiofiles.open(temp_file, "wb") as f:
                            await f.write(response.content)

                        self.logger.info(
                            f"Downloaded image {i + 1}/{len(image_urls)}: {os.path.basename(temp_file)}",
                        )
                        break

                    except Exception as e:
                        self.logger.warning(
                            f"Download attempt {attempt + 1} failed for {url}: {e}",
                        )
                        if attempt < max_retries - 1:
                            wait_time = 2**attempt  # Exponential backoff
                            await asyncio.sleep(wait_time)
                        else:
                            self.logger.error(
                                f"Failed to download {url} after {max_retries} attempts",
                            )

        return temp_files

    async def _wait_for_upload_completion(
        self,
        expected_count: int,
        timeout: int | None = None,
    ) -> bool:
        """Wait for all image uploads to complete"""
        try:
            # Use configured timeout or provided override
            effective_timeout = timeout if timeout is not None else self.upload_timeout

            # Validate timeout value
            if effective_timeout < 60:
                self.logger.warning(
                    f"Upload timeout {effective_timeout}s is too low, using minimum 60s",
                )
                effective_timeout = 60

            self.logger.debug(f"Using upload timeout: {effective_timeout}s")

            # Wait for upload indicators to appear
            upload_progress = '[role="progressbar"]'
            upload_complete = '[data-testid="marketplace-composer-photo-preview"]'

            # Wait for progress indicators to disappear (uploads completing)
            page = self._ensure_page()
            start_time = asyncio.get_event_loop().time()

            while True:
                current_time = asyncio.get_event_loop().time()
                if current_time - start_time > effective_timeout:
                    self.logger.warning(f"Upload timeout after {effective_timeout}s")
                    return False

                # Check if upload spinners are still present
                if await page.locator(upload_progress).count() == 0:
                    # Check if we have the expected number of uploaded images
                    uploaded_count = await page.locator(upload_complete).count()
                    if uploaded_count >= expected_count:
                        self.logger.info(
                            f"All {uploaded_count} images uploaded successfully",
                        )
                        return True

                await asyncio.sleep(1)

        except Exception as e:
            self.logger.error(f"Error waiting for upload completion: {e}")
            return False

    async def _cleanup_temp_files(self, temp_files: list[str]) -> None:
        """Clean up temporary image files"""
        for temp_file in temp_files:
            try:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
                    self.logger.debug(f"Cleaned up temporary file: {temp_file}")
            except Exception as e:
                self.logger.warning(f"Failed to clean up {temp_file}: {e}")

    def _get_image_extension(self, url: str) -> str:
        """Extract image extension from URL or default to .jpg"""
        common_extensions = [".jpg", ".jpeg", ".png", ".gif", ".webp"]
        url_lower = url.lower()

        for ext in common_extensions:
            if ext in url_lower:
                return ext

        return ".jpg"  # Default fallback

    async def _extract_listing_url(self) -> str | None:
        """Extract the URL of the created listing"""
        try:
            page = self._ensure_page()
            # Wait for redirect to listing page
            await page.wait_for_load_state("networkidle", timeout=10000)
            current_url = page.url

            # Check if we're on a marketplace listing page
            if "/marketplace/item/" in current_url:
                return current_url

            # Alternative: look for link in success modal
            try:
                link_element = page.locator('a[href*="/marketplace/item/"]').first
                if await link_element.is_visible():
                    return await link_element.get_attribute("href")
            except Exception as e:
                self.logger.debug(f"Could not find marketplace link in modal: {e}")

            return None

        except Exception as e:
            self.logger.error(f"Error extracting listing URL: {e}")
            return None

    def _generate_facebook_id(self) -> str:
        """Generate a Facebook-style listing ID"""
        return f"fb_{int(time.time())}"

    async def _check_for_errors(self) -> list[str]:
        """Check for Facebook-specific error messages"""
        error_messages = []

        try:
            # Common error selectors
            error_selectors = [
                '[data-testid="marketplace-error-message"]',
                ".error-message",
                '[role="alert"]',
                'text="There was a problem"',
                'text="Error"',
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
        """Validate Facebook credentials"""
        try:
            return await self.login(credentials)
        except Exception as e:
            self.logger.error(f"Credential validation failed: {e}")
            return False

    def get_supported_categories(self) -> list[str]:
        """Get supported Facebook Marketplace categories"""
        return list(self.category_mapping.keys())
