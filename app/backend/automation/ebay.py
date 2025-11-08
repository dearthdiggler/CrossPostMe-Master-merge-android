"""eBay automation using the eBay Developer API
Handles posting items to eBay through their official Trading API
"""

import xml.etree.ElementTree as ET
from typing import Any

import httpx

from .base import (
    AdData,
    PlatformAutomationBase,
    PlatformCredentials,
    PostResult,
    PostStatus,
)


class EBayAutomation(PlatformAutomationBase):
    """eBay posting automation using Trading API"""

    def __init__(self, headless: bool = True):
        super().__init__(
            "ebay",
            headless,
            rate_limit=0.1,
        )  # 0.1 requests per second for API

        # eBay API endpoints
        self.sandbox_url = "https://api.sandbox.ebay.com/ws/api/eBayAPI/xml"
        self.production_url = "https://api.ebay.com/ws/api/eBayAPI/xml"

        # Use sandbox by default (change to production_url for live)
        self.api_url = self.sandbox_url

        # API version
        self.api_version = "967"

        # eBay site ID (0 = US, 3 = UK, etc.)
        self.site_id = "0"

        # Category mapping for eBay
        self.category_mapping = {
            "electronics": "293",  # Consumer Electronics
            "furniture": "20081",  # Home & Garden > Furniture
            "vehicles": "6001",  # eBay Motors > Cars & Trucks
            "real estate": "10542",  # Real Estate
            "appliances": "20710",  # Home & Garden > Major Appliances
            "clothing": "11450",  # Clothing, Shoes & Accessories
            "sports": "888",  # Sporting Goods
            "tools": "631",  # Business & Industrial > Tools
            "other": "99",  # Everything Else
        }

        # Listing durations (days)
        self.listing_durations = {
            "auction": ["1", "3", "5", "7", "10"],
            "fixed_price": ["GTC"],  # Good Till Cancelled
        }

        # Required API credentials
        self.app_id: str | None = None
        self.dev_id: str | None = None
        self.cert_id: str | None = None
        self.user_token: str | None = None

    def configure_api_credentials(
        self,
        app_id: str,
        dev_id: str,
        cert_id: str,
        user_token: str,
        use_production: bool = False,
    ) -> None:
        """Configure eBay API credentials"""
        self.app_id = app_id
        self.dev_id = dev_id
        self.cert_id = cert_id
        self.user_token = user_token

        if use_production:
            self.api_url = self.production_url
        else:
            self.api_url = self.sandbox_url

    async def login(self, credentials: PlatformCredentials) -> bool:
        """Validate eBay API credentials (no traditional login needed)"""
        try:
            # Extract API credentials from the credentials object
            if credentials.additional_data:
                self.app_id = credentials.additional_data.get("app_id")
                self.dev_id = credentials.additional_data.get("dev_id")
                self.cert_id = credentials.additional_data.get("cert_id")
                self.user_token = credentials.additional_data.get("user_token")

            # Validate credentials by making a test API call
            return await self._validate_api_credentials()

        except Exception as e:
            self.logger.error(f"eBay credential validation failed: {e}")
            return False

    async def _validate_api_credentials(self) -> bool:
        """Validate eBay API credentials with test call"""
        try:
            # Use GeteBayOfficialTime as a simple test call
            xml_request = self._build_xml_request("GeteBayOfficialTime")

            response = await self._make_api_call(xml_request)

            if response and "eBayOfficialTime" in response:
                self.logger.info("eBay API credentials validated")
                return True

            return False

        except Exception as e:
            self.logger.error(f"API credential validation failed: {e}")
            return False

    async def post_ad(
        self,
        ad_data: AdData,
        credentials: PlatformCredentials,
    ) -> PostResult:
        """Post item to eBay using Trading API"""
        try:
            # Validate credentials first
            if not await self.login(credentials):
                return PostResult(
                    status=PostStatus.LOGIN_REQUIRED,
                    message="Invalid eBay API credentials",
                )

            # Create the listing
            return await self._create_ebay_listing(ad_data)

        except Exception as e:
            self.logger.error(f"Error posting to eBay: {e}")
            return PostResult(status=PostStatus.FAILED, message=str(e))

    async def _create_ebay_listing(self, ad_data: AdData) -> PostResult:
        """Create eBay listing using AddItem API call"""
        try:
            # Build the AddItem XML request
            xml_request = self._build_add_item_request(ad_data)

            # Make the API call
            response = await self._make_api_call(xml_request)

            # Parse response
            return self._parse_add_item_response(response)

        except Exception as e:
            self.logger.error(f"Error creating eBay listing: {e}")
            return PostResult(status=PostStatus.FAILED, message=str(e))

    def _build_xml_request(self, call_name: str, body_content: str = "") -> str:
        """Build XML request with eBay API headers"""
        xml = f"""<?xml version="1.0" encoding="utf-8"?>
<{call_name}Request xmlns="urn:ebay:apis:eBLBaseComponents">
  <RequesterCredentials>
    <eBayAuthToken>{self.user_token}</eBayAuthToken>
  </RequesterCredentials>
  <Version>{self.api_version}</Version>
  {body_content}
</{call_name}Request>"""

        return xml

    def _build_add_item_request(self, ad_data: AdData) -> str:
        """Build AddItem XML request for eBay listing"""
        # Get category ID
        category_id = self.category_mapping.get(ad_data.category.lower(), "99")

        # Build item XML
        item_xml = f"""
        <Item>
          <Title>{self._escape_xml(ad_data.title)}</Title>
          <Description><![CDATA[{ad_data.description}]]></Description>
          <PrimaryCategory>
            <CategoryID>{category_id}</CategoryID>
          </PrimaryCategory>
          <StartPrice>{ad_data.price:.2f}</StartPrice>
          <CategoryMappingAllowed>true</CategoryMappingAllowed>
          <Country>US</Country>
          <Currency>USD</Currency>
          <DispatchTimeMax>3</DispatchTimeMax>
          <ListingDuration>GTC</ListingDuration>
          <ListingType>FixedPriceItem</ListingType>
          <PaymentMethods>PayPal</PaymentMethods>
          <PaymentMethods>VisaMC</PaymentMethods>
          <PaymentMethods>AmEx</PaymentMethods>
          <PostalCode>85001</PostalCode>
          <Quantity>1</Quantity>
          <ReturnPolicy>
            <ReturnsAcceptedOption>ReturnsAccepted</ReturnsAcceptedOption>
            <RefundOption>MoneyBack</RefundOption>
            <ReturnsWithinOption>Days_30</ReturnsWithinOption>
            <ShippingCostPaidByOption>Buyer</ShippingCostPaidByOption>
          </ReturnPolicy>
          <ShippingDetails>
            <ShippingType>Flat</ShippingType>
            <ShippingServiceOptions>
              <ShippingServicePriority>1</ShippingServicePriority>
              <ShippingService>USPSMedia</ShippingService>
              <ShippingServiceCost>5.99</ShippingServiceCost>
            </ShippingServiceOptions>
          </ShippingDetails>
          <Site>US</Site>
        </Item>"""

        return self._build_xml_request("AddItem", item_xml)

    def _escape_xml(self, text: str) -> str:
        """Escape XML special characters"""
        if not text:
            return ""

        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&apos;")
        )

    async def _make_api_call(self, xml_request: str) -> dict[str, Any] | None:
        """Make eBay API call"""
        try:
            # Ensure all header values are strings (httpx expects Mapping[str, str])
            headers = {
                "X-EBAY-API-COMPATIBILITY-LEVEL": str(self.api_version),
                "X-EBAY-API-DEV-NAME": str(self.dev_id or ""),
                "X-EBAY-API-APP-NAME": str(self.app_id or ""),
                "X-EBAY-API-CERT-NAME": str(self.cert_id or ""),
                "X-EBAY-API-SITEID": str(self.site_id),
                "X-EBAY-API-CALL-NAME": str(self._extract_call_name(xml_request)),
                "Content-Type": "text/xml",
            }

            # Make the async HTTP request using httpx
            async with httpx.AsyncClient() as client:
                # use `content=` to make the intent explicit for httpx and help stubs
                response = await client.post(
                    self.api_url,
                    content=xml_request,
                    headers=headers,
                    timeout=30,
                )

            if response.status_code == 200:
                return self._parse_xml_response(response.text)
            self.logger.error(
                f"eBay API error: {response.status_code} - {response.text}",
            )
            return None

        except Exception as e:
            self.logger.error(f"eBay API call failed: {e}")
            return None

    def _extract_call_name(self, xml_request: str) -> str:
        """Extract API call name from XML request"""
        try:
            # Parse XML to get the root element name
            root = ET.fromstring(xml_request)
            call_name = root.tag.split("}")[-1]  # Remove namespace
            return call_name.replace("Request", "")
        except Exception:
            return "AddItem"  # Default fallback

    def _parse_xml_response(self, xml_text: str) -> dict[str, Any] | None:
        """Parse eBay XML response to dictionary"""
        try:
            root = ET.fromstring(xml_text)

            # Convert XML to dictionary (simplified)
            result: dict[str, Any] = {}

            for child in root:
                tag = child.tag.split("}")[-1]  # Remove namespace
                result[tag] = child.text or ""

            return result

        except Exception as e:
            self.logger.error(f"Error parsing eBay XML response: {e}")
            return None

    def _parse_add_item_response(self, response: dict[str, Any] | None) -> PostResult:
        """Parse AddItem API response"""
        try:
            if not response:
                return PostResult(
                    status=PostStatus.FAILED,
                    message="No response from eBay API",
                )

            # Check for success
            ack = response.get("Ack", "")
            if ack in ["Success", "Warning"]:
                item_id = response.get("ItemID", "")
                listing_url = f"https://www.ebay.com/itm/{item_id}" if item_id else None

                return PostResult(
                    status=PostStatus.SUCCESS,
                    platform_ad_id=item_id,
                    post_url=listing_url,
                    message=f"Successfully listed on eBay with ID: {item_id}",
                )

            # Handle errors
            errors = response.get("Errors", "")
            if errors:
                return PostResult(
                    status=PostStatus.FAILED,
                    message=f"eBay listing failed: {errors}",
                )

            return PostResult(
                status=PostStatus.FAILED,
                message="Unknown eBay API error",
            )

        except Exception as e:
            self.logger.error(f"Error parsing eBay response: {e}")
            return PostResult(status=PostStatus.FAILED, message=str(e))

    async def validate_credentials(self, credentials: PlatformCredentials) -> bool:
        """Validate eBay API credentials"""
        try:
            return await self.login(credentials)
        except Exception as e:
            self.logger.error(f"eBay credential validation failed: {e}")
            return False

    def get_supported_categories(self) -> list[str]:
        """Get supported eBay categories"""
        return list(self.category_mapping.keys())

    # Additional eBay-specific methods

    async def get_categories(self) -> list[dict[str, Any]] | None:
        """Get eBay categories using GetCategories API"""
        try:
            xml_request = self._build_xml_request(
                "GetCategories",
                "<DetailLevel>ReturnAll</DetailLevel>",
            )

            response = await self._make_api_call(xml_request)

            if response:
                # Parse categories from response
                # This is a simplified version - you'd need to parse the full XML
                return [{"id": k, "name": v} for k, v in self.category_mapping.items()]

            return None

        except Exception as e:
            self.logger.error(f"Error getting eBay categories: {e}")
            return None

    async def revise_item(self, item_id: str, ad_data: AdData) -> PostResult:
        """Revise existing eBay item using ReviseItem API"""
        try:
            item_xml = f"""
            <Item>
              <ItemID>{item_id}</ItemID>
              <Title>{self._escape_xml(ad_data.title)}</Title>
              <Description><![CDATA[{ad_data.description}]]></Description>
              <StartPrice>{ad_data.price:.2f}</StartPrice>
            </Item>"""

            xml_request = self._build_xml_request("ReviseItem", item_xml)
            response = await self._make_api_call(xml_request)

            if response and response.get("Ack") in ["Success", "Warning"]:
                return PostResult(
                    status=PostStatus.SUCCESS,
                    platform_ad_id=item_id,
                    message="Successfully revised eBay listing",
                )

            return PostResult(
                status=PostStatus.FAILED,
                message="Failed to revise eBay listing",
            )

        except Exception as e:
            self.logger.error(f"Error revising eBay item: {e}")
            return PostResult(status=PostStatus.FAILED, message=str(e))

    async def end_item(self, item_id: str, reason: str = "NotAvailable") -> PostResult:
        """End eBay listing using EndItem API"""
        try:
            item_xml = f"""
            <ItemID>{item_id}</ItemID>
            <EndingReason>{reason}</EndingReason>"""

            xml_request = self._build_xml_request("EndItem", item_xml)
            response = await self._make_api_call(xml_request)

            if response and response.get("Ack") in ["Success", "Warning"]:
                return PostResult(
                    status=PostStatus.SUCCESS,
                    platform_ad_id=item_id,
                    message="Successfully ended eBay listing",
                )

            return PostResult(
                status=PostStatus.FAILED,
                message="Failed to end eBay listing",
            )

        except Exception as e:
            self.logger.error(f"Error ending eBay item: {e}")
            return PostResult(status=PostStatus.FAILED, message=str(e))
