"""Craigslist automation
Handles posting ads to Craigslist with account rotation and anti-detection
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


class CraigslistAutomation(PlatformAutomationBase):
    """Craigslist posting automation"""

    def __init__(self, headless: bool = True):
        super().__init__(
            "craigslist",
            headless,
            rate_limit=0.2,
        )  # 0.2 requests per second

        self.base_url = "https://craigslist.org"

        # Category mapping for Craigslist
        self.category_mapping = {
            "electronics": "ela",  # electronics
            "furniture": "fua",  # furniture
            "vehicles": "cta",  # cars & trucks
            "real estate": "rea",  # real estate
            "appliances": "app",  # appliances
            "clothing": "cla",  # clothing & accessories
            "sports": "sga",  # sporting goods
            "tools": "tla",  # tools
            "other": "foa",  # for sale - other
        }

        # Location mapping (you'd expand this for more cities)
        self.location_mapping = {
            "phoenix": "phoenix.craigslist.org",
            "los angeles": "losangeles.craigslist.org",
            "new york": "newyork.craigslist.org",
            "chicago": "chicago.craigslist.org",
            "houston": "houston.craigslist.org",
            "philadelphia": "philadelphia.craigslist.org",
            "san antonio": "sanantonio.craigslist.org",
            "san diego": "sandiego.craigslist.org",
            "dallas": "dallas.craigslist.org",
            "san jose": "sfbay.craigslist.org",
        }

    def _get_craigslist_domain(self, location: str) -> str:
        """Get the appropriate Craigslist domain for a location"""
        location_lower = location.lower()

        # Check for exact matches first
        for city, domain in self.location_mapping.items():
            if city in location_lower:
                return domain

        # Default to Phoenix if no match found
        return "phoenix.craigslist.org"

    async def login(self, credentials: PlatformCredentials) -> bool:
        """Login to Craigslist (if account exists)"""
        try:
            # Craigslist doesn't require login for posting in many areas
            # but having an account can help with posting limits

            domain = self._get_craigslist_domain("phoenix")  # Default domain for login
            login_url = f"https://{domain}/login"

            self.logger.info("Navigating to Craigslist login")
            await self.goto(login_url)
            await self.random_delay(2, 4)

            # Check if login form exists
            try:
                await self.wait_for_selector(
                    'input[name="inputEmailHandle"]',
                    timeout=5000,
                )
            except Exception:
                # No login form, assume anonymous posting is allowed
                self.logger.info("No login required, using anonymous posting")
                return True

            # Fill email/username
            email_input = 'input[name="inputEmailHandle"]'
            if not await self.safe_fill(email_input, credentials.username):
                return False

            # Fill password
            password_input = 'input[name="inputPassword"]'
            if not await self.safe_fill(password_input, credentials.password):
                return False

            # Click login button
            login_button = 'input[type="submit"][value="log in"]'
            if not await self.safe_click(login_button):
                return False

            await self.random_delay(2, 4)

            # Check for login success (look for account indicators)
            try:
                await self.wait_for_selector('a[href="/login/home"]', timeout=5000)
                self.logger.info("Successfully logged in to Craigslist")
                return True
            except Exception:
                # Login may have failed, but anonymous posting might still work
                self.logger.warning("Login unsuccessful, attempting anonymous posting")
                return True

        except Exception as e:
            self.logger.error(f"Login process failed: {e}")
            return False

    async def post_ad(
        self,
        ad_data: AdData,
        credentials: PlatformCredentials,
    ) -> PostResult:
        """Post ad to Craigslist"""
        try:
            # Get appropriate domain for the location
            domain = self._get_craigslist_domain(ad_data.location)
            post_url = f"https://{domain}/post"

            self.logger.info(f"Posting to {domain}")
            await self.goto(post_url)
            await self.random_delay(2, 4)

            # Handle CAPTCHA if present
            if not await self.wait_and_handle_captcha():
                return PostResult(
                    status=PostStatus.CAPTCHA_REQUIRED,
                    message="CAPTCHA required",
                )

            # Navigate through Craigslist posting flow
            return await self._navigate_posting_flow(ad_data)

        except Exception as e:
            self.logger.error(f"Error posting ad: {e}")
            return PostResult(status=PostStatus.FAILED, message=str(e))

    async def _navigate_posting_flow(self, ad_data: AdData) -> PostResult:
        """Navigate through Craigslist's multi-step posting flow"""
        try:
            # Step 1: Select "for sale" category
            sale_category = 'input[value="sss"]'  # for sale by owner
            loc = self.locator(sale_category)
            if await loc.is_visible(timeout=10000):
                await self.safe_click(sale_category)
                await self.safe_click('button[type="submit"]')
                await self.random_delay(1, 2)

            # Step 2: Select specific category
            category_code = self.category_mapping.get(ad_data.category.lower(), "foa")
            category_selector = f'input[value="{category_code}"]'

            loc = self.locator(category_selector)
            if await loc.is_visible(timeout=10000):
                await self.safe_click(category_selector)
                await self.safe_click('button[type="submit"]')
                await self.random_delay(1, 2)

            # Step 3: Fill the posting form
            return await self._fill_posting_form(ad_data)

        except Exception as e:
            self.logger.error(f"Error navigating posting flow: {e}")
            return PostResult(status=PostStatus.FAILED, message=str(e))

    async def _fill_posting_form(self, ad_data: AdData) -> PostResult:
        """Fill the Craigslist posting form"""
        try:
            # Wait for posting form
            await self.wait_for_selector("#postingForm", timeout=15000)
            await self.random_delay(1, 2)

            # Fill title
            title_input = 'input[name="PostingTitle"]'
            if not await self.safe_fill(title_input, ad_data.title):
                return PostResult(
                    status=PostStatus.FAILED,
                    message="Failed to fill title",
                )

            # Fill price
            price_input = 'input[name="price"]'
            loc = self.locator(price_input)
            if await loc.is_visible():
                if not await self.safe_fill(price_input, str(int(ad_data.price))):
                    return PostResult(
                        status=PostStatus.FAILED,
                        message="Failed to fill price",
                    )

            # Fill description
            description_textarea = 'textarea[name="PostingBody"]'
            if not await self.safe_fill(description_textarea, ad_data.description):
                return PostResult(
                    status=PostStatus.FAILED,
                    message="Failed to fill description",
                )

            # Handle location/area selection
            await self._handle_location_selection(ad_data.location)

            # Fill contact information
            if ad_data.contact_info:
                await self._fill_contact_info(ad_data.contact_info)

            # Upload images if provided
            if ad_data.images:
                await self._upload_images(ad_data.images)

            # Submit the form
            continue_button = 'input[value="continue"]'
            if not await self.safe_click(continue_button):
                return PostResult(
                    status=PostStatus.FAILED,
                    message="Failed to submit form",
                )

            await self.random_delay(2, 4)

            # Handle preview and final submission
            return await self._handle_preview_and_submit()

        except Exception as e:
            self.logger.error(f"Error filling form: {e}")
            return PostResult(status=PostStatus.FAILED, message=str(e))

    async def _handle_location_selection(self, location: str) -> bool:
        """Handle Craigslist location/area selection"""
        try:
            # Look for area selection dropdown
            area_select = 'select[name="area"]'
            loc = self.locator(area_select)
            if await loc.is_visible():
                # Try to match the location to an area option
                option_loc = self.locator(f"{area_select} option")
                options = await option_loc.all()
                location_lower = location.lower()

                matched_index = 0  # Default to first
                exact_match_index = None
                for i, option in enumerate(options):
                    text = await option.text_content()
                    if text:
                        text_lower = text.lower().strip()
                        # Check for exact match first
                        if location_lower == text_lower:
                            exact_match_index = i
                            self.logger.info(
                                f"Exact match for location '{location}': {text}",
                            )
                            break
                        if location_lower in text_lower and matched_index == 0:
                            # Keep first substring match as fallback
                            matched_index = i
                            self.logger.info(
                                f"Substring match for location '{location}': {text}",
                            )

                # Prefer exact match over substring match
                if exact_match_index is not None:
                    matched_index = exact_match_index

                await self.select_option(area_select, index=matched_index)
                await self.random_delay(0.5, 1.0)

            return True

        except Exception as e:
            self.logger.error(f"Error handling location selection: {e}")
            return False

    async def _fill_contact_info(self, contact_info: dict[str, str]) -> bool:
        """Fill contact information"""
        try:
            # Email
            email = contact_info.get("email")
            if email:
                email_input = 'input[name="FromEMail"]'
                loc = self.locator(email_input)
                if await loc.is_visible():
                    await self.safe_fill(email_input, email)

            # Phone
            phone = contact_info.get("phone")
            if phone:
                phone_input = 'input[name="PhoneNumber"]'
                loc = self.locator(phone_input)
                if await loc.is_visible():
                    await self.safe_fill(phone_input, phone)

            return True

        except Exception as e:
            self.logger.error(f"Error filling contact info: {e}")
            return False

    async def _upload_images(self, image_urls: list[str]) -> bool:
        """Upload images to Craigslist listing"""
        if not image_urls:
            return True

        temp_files = []
        try:
            # Craigslist allows file uploads
            file_input = 'input[type="file"]'

            loc = self.locator(file_input)
            if await loc.is_visible():
                self.logger.info(
                    f"Image upload available - downloading {len(image_urls)} images",
                )

                # Step 1: Download images to temporary files
                temp_files = await self._download_images_for_upload(image_urls)

                if not temp_files:
                    self.logger.warning("No images successfully downloaded for upload")
                    return False

                # Step 2: Upload files using Playwright
                self.logger.info(f"Uploading {len(temp_files)} images to Craigslist")
                file_loc = self.locator(file_input)
                await file_loc.set_input_files(temp_files)

                # Step 3: Wait for upload completion
                await self._wait_for_craigslist_upload_completion(len(temp_files))

                self.logger.info(f"Successfully uploaded {len(temp_files)} images")
                return True
            self.logger.warning("File input not found - skipping image upload")
            return False

        except Exception as e:
            self.logger.error(f"Image upload failed: {e}")
            return False
        finally:
            # Step 4: Clean up temporary files
            await self._cleanup_temp_files(temp_files)

    async def _download_images_for_upload(
        self,
        image_urls: list[str],
        timeout: int = 120,
        max_retries: int = 3,
    ) -> list[str]:
        """Download images to temporary files for Craigslist upload"""
        temp_files = []

        async with httpx.AsyncClient(timeout=timeout) as client:
            for i, url in enumerate(image_urls):
                # Create temp file once per image (outside retry loop)
                temp_dir = tempfile.gettempdir()
                file_extension = self._get_image_extension_from_url(url)
                temp_file = os.path.join(
                    temp_dir,
                    f"craigslist_upload_{i}{file_extension}",
                )

                # Add to tracking list for cleanup
                temp_files.append(temp_file)

                for attempt in range(max_retries):
                    try:
                        self.logger.debug(
                            f"Downloading {url} to {temp_file} (attempt {attempt + 1})",
                        )

                        # Use streaming download for large files
                        async with client.stream("GET", url) as response:
                            response.raise_for_status()

                            async with aiofiles.open(temp_file, "wb") as f:
                                async for chunk in response.aiter_bytes():
                                    await f.write(chunk)

                        # Verify file was created and has content
                        if os.path.exists(temp_file) and os.path.getsize(temp_file) > 0:
                            self.logger.info(
                                f"Downloaded image {i + 1}/{len(image_urls)}: {os.path.basename(temp_file)}",
                            )
                            break
                        raise Exception("Downloaded file is empty or missing")

                    except Exception as e:
                        self.logger.warning(
                            f"Download attempt {attempt + 1} failed for {url}: {e}",
                        )

                        # Clean up failed partial download
                        if os.path.exists(temp_file):
                            try:
                                os.unlink(temp_file)
                            except Exception as e:
                                self.logger.error(
                                    f"Failed to cleanup temp file {temp_file}: {e}",
                                )
                                # Continue silently to avoid disrupting the retry flow

                        if attempt < max_retries - 1:
                            wait_time = 2**attempt  # Exponential backoff
                            await asyncio.sleep(wait_time)
                        else:
                            self.logger.error(
                                f"Failed to download {url} after {max_retries} attempts - skipping",
                            )
                            # Remove from temp_files list if download completely failed
                            if temp_file in temp_files:
                                temp_files.remove(temp_file)

        # Return only successfully downloaded files
        valid_files = [
            f for f in temp_files if os.path.exists(f) and os.path.getsize(f) > 0
        ]
        return valid_files

    async def _wait_for_craigslist_upload_completion(
        self,
        expected_count: int,
        timeout: int = 60,
    ) -> bool:
        """Wait for Craigslist image uploads to complete"""
        try:
            # Look for upload progress indicators or completion signs

            start_time = asyncio.get_event_loop().time()

            while True:
                current_time = asyncio.get_event_loop().time()
                if current_time - start_time > timeout:
                    self.logger.warning(f"Upload timeout after {timeout}s")
                    return False

                # Check if uploads appear to be complete
                # Craigslist typically shows uploaded images or enables continue button
                locator_btn = self.locator(
                    'button[type="submit"], input[value="continue"]'
                )
                continue_button = await locator_btn.count()
                if continue_button > 0:
                    # Check if button is enabled (uploads complete)
                    page = self._ensure_page()
                    button = page.locator(
                        'button[type="submit"], input[value="continue"]',
                    ).first
                    if await button.is_enabled():
                        self.logger.info(
                            "Upload appears complete - continue button enabled",
                        )
                        return True

                await asyncio.sleep(2)  # Check every 2 seconds

        except Exception:
            self.logger.exception("Error waiting for upload completion")
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

    def _get_image_extension_from_url(self, url: str) -> str:
        """Extract image extension from URL or default to .jpg"""
        common_extensions = [".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"]
        url_lower = url.lower()

        for ext in common_extensions:
            if ext in url_lower:
                return ext

        return ".jpg"  # Default fallback

    async def _handle_preview_and_submit(self) -> PostResult:
        """Handle the preview page and final submission"""
        try:
            # Wait for preview page
            await self.wait_for_load_state("networkidle", timeout=10000)

            # Look for publish button on preview page
            publish_selectors = [
                'input[value="publish"]',
                'input[value="PUBLISH"]',
                'button:has-text("publish")',
                'input[type="submit"][value*="publish"]',
            ]

            for selector in publish_selectors:
                loc = self.locator(selector)
                if await loc.is_visible(timeout=5000):
                    await self.safe_click(selector)
                    await self.random_delay(3, 5)
                    break

            # Check for success confirmation
            success_indicators = [
                'text="Your posting is live"',
                'text="Thank you for your submission"',
                'text="Your ad has been posted"',
                ".posted_success",
            ]

            for selector in success_indicators:
                loc = self.locator(selector)
                if await loc.is_visible(timeout=10000):
                    # Try to extract posting URL
                    posting_url = await self._extract_posting_url()

                    return PostResult(
                        status=PostStatus.SUCCESS,
                        post_url=posting_url,
                        platform_ad_id=self._generate_craigslist_id(),
                        message="Successfully posted to Craigslist",
                    )

            # Check for errors
            error_messages = await self._check_for_errors()
            if error_messages:
                return PostResult(
                    status=PostStatus.FAILED,
                    message=f"Craigslist errors: {', '.join(error_messages)}",
                )

            return PostResult(
                status=PostStatus.FAILED,
                message="Posting status unknown - may require manual verification",
            )

        except Exception as e:
            self.logger.error(f"Error in preview/submit: {e}")
            return PostResult(status=PostStatus.FAILED, message=str(e))

    async def _extract_posting_url(self) -> str | None:
        """Extract the URL of the created posting"""
        try:
            page = self._ensure_page()
            current_url = page.url

            # Craigslist posting URLs typically follow pattern:
            # https://city.craigslist.org/category/d/title/postid.html
            if ".craigslist.org" in current_url and "/d/" in current_url:
                return current_url

            # Look for links to the posting
            link_patterns = [
                'a[href*=".craigslist.org"][href*="/d/"]',
                'a:has-text("view your posting")',
            ]

            for pattern in link_patterns:
                link = page.locator(pattern).first
                if await link.is_visible():
                    href = await link.get_attribute("href")
                    if href and ".craigslist.org" in href:
                        return href

            return None

        except Exception as e:
            self.logger.error(f"Error extracting posting URL: {e}")
            return None

    def _generate_craigslist_id(self) -> str:
        """Generate a Craigslist-style posting ID"""
        return f"cl_{int(time.time())}"

    async def _check_for_errors(self) -> list[str]:
        """Check for Craigslist-specific error messages"""
        error_messages = []

        try:
            error_selectors = [
                ".error",
                ".errortext",
                'text="blocked"',
                'text="prohibited"',
                'text="invalid"',
                'font[color="red"]',
            ]

            for selector in error_selectors:
                loc = self.locator(selector)
                elements = await loc.all()
                for element in elements:
                    if await element.is_visible():
                        text = await element.text_content()
                        if text and text.strip():
                            error_messages.append(text.strip())

        except Exception as e:
            self.logger.error(f"Error checking for errors: {e}")

        return error_messages

    async def validate_credentials(self, credentials: PlatformCredentials) -> bool:
        """Validate Craigslist credentials"""
        try:
            return await self.login(credentials)
        except Exception as e:
            self.logger.error(f"Credential validation failed: {e}")
            return False

    def get_supported_categories(self) -> list[str]:
        """Get supported Craigslist categories"""
        return list(self.category_mapping.keys())
