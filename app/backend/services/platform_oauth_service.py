"""Platform OAuth Integration Service
Handles OAuth flows for marketplace platforms: OfferUp, Facebook, Craigslist, eBay
"""

import base64
import json
import logging
import os
import secrets
from datetime import datetime, timedelta
from typing import Any
from urllib.parse import urlencode

import httpx
from cryptography.fernet import Fernet, InvalidToken
from fastapi import HTTPException

logger = logging.getLogger(__name__)


class PlatformOAuthService:
    """Service for handling OAuth integrations with marketplace platforms"""

    def __init__(self, db: Any) -> None:
        # db is a motor/Mongo-like client / collection accessor; keep as Any for now
        self.db: Any = db

        # Initialize encryption for credential storage
        self._init_encryption()

        # OAuth Configuration for each platform
        self.oauth_configs: dict[str, dict[str, Any]] = {
            "facebook": {
                "client_id": None,  # Set via environment variables
                "client_secret": None,
                "scope": "pages_manage_posts,pages_read_engagement,marketplace_management",
                "auth_url": "https://www.facebook.com/v18.0/dialog/oauth",
                "token_url": "https://graph.facebook.com/v18.0/oauth/access_token",
                "api_base": "https://graph.facebook.com/v18.0",
            },
            "ebay": {
                "client_id": None,
                "client_secret": None,
                "scope": "https://api.ebay.com/oauth/api_scope/sell.marketing https://api.ebay.com/oauth/api_scope/sell.inventory",
                "auth_url": "https://auth.ebay.com/oauth2/authorize",
                "token_url": "https://api.ebay.com/identity/v1/oauth2/token",
                "api_base": "https://api.ebay.com",
            },
            "offerup": {
                # Note: OfferUp doesn't have public OAuth API
                # This would need to be implemented via web scraping or unofficial methods
                "note": "OfferUp requires custom integration - no public OAuth API",
                "method": "credential_storage",  # Store username/password securely
            },
            "craigslist": {
                # Note: Craigslist doesn't have OAuth API
                # This would need credential storage and automated posting
                "note": "Craigslist requires custom integration - no OAuth API",
                "method": "credential_storage",  # Store account credentials securely
            },
        }

        # Validate OAuth configuration at initialization
        self._validate_oauth_config()

    def _init_encryption(self) -> None:
        """Initialize encryption for credential storage"""
        encryption_key = os.getenv("CREDENTIAL_ENCRYPTION_KEY")
        environment = os.getenv("ENVIRONMENT", "production").lower()
        debug_mode = os.getenv("DEBUG", "false").lower() in ("true", "1", "yes")

        if not encryption_key:
            # In production, encryption key is required
            if environment == "production" or not debug_mode:
                logger.error(
                    "CREDENTIAL_ENCRYPTION_KEY is required but not found in environment variables",
                )
                raise HTTPException(
                    status_code=500,
                    detail="Server configuration error: Missing required encryption configuration.",
                )

            # For development/debug mode only: generate temporary key
            logger.warning(
                "CREDENTIAL_ENCRYPTION_KEY not found. Using temporary key for development.",
            )
            print("\n" + "=" * 80)
            print("WARNING: CREDENTIAL_ENCRYPTION_KEY not configured!")
            print("This is only allowed in development mode.")
            print("To generate a permanent key, run:")
            print(
                "  python -c \"from cryptography.fernet import Fernet; print('CREDENTIAL_ENCRYPTION_KEY=' + Fernet.generate_key().decode())\"",
            )
            print("Then add the key to your environment variables.")
            print("=" * 80 + "\n")

            # Generate temporary in-memory key (will be lost on restart)
            encryption_key = Fernet.generate_key().decode()

        try:
            # Validate the encryption key format and normalize to bytes
            if isinstance(encryption_key, str):
                key_bytes: bytes = encryption_key.encode()
            elif isinstance(encryption_key, bytes):
                key_bytes = encryption_key
            else:
                # Fallback - generate a temporary key
                key_bytes = Fernet.generate_key()

            # Test key validity by creating cipher instance
            self.cipher = Fernet(key_bytes)

            # Test encryption/decryption to ensure key works
            test_data = b"test"
            encrypted = self.cipher.encrypt(test_data)
            decrypted = self.cipher.decrypt(encrypted)

            if decrypted != test_data:
                raise ValueError(
                    "Encryption key validation failed: decrypt test mismatch",
                )

            logger.info("Credential encryption initialized successfully")

        except ValueError as e:
            logger.error(f"Invalid CREDENTIAL_ENCRYPTION_KEY format or value: {e!s}")
            raise HTTPException(
                status_code=500,
                detail="Invalid encryption key configuration. Please check CREDENTIAL_ENCRYPTION_KEY format.",
            ) from e
        except Exception as e:
            logger.error(
                f"Failed to initialize credential encryption: {type(e).__name__}: {e!s}",
            )
            raise HTTPException(
                status_code=500,
                detail="Credential encryption initialization failed. Please check server configuration.",
            ) from e

    def _validate_oauth_config(self) -> None:
        """Validate OAuth configuration and log missing credentials"""
        import os

        required_env_vars = {
            "facebook": ["FACEBOOK_CLIENT_ID", "FACEBOOK_CLIENT_SECRET"],
            "ebay": ["EBAY_CLIENT_ID", "EBAY_CLIENT_SECRET"],
        }

        missing_vars = []
        for platform, vars_list in required_env_vars.items():
            for var in vars_list:
                if not os.getenv(var):
                    missing_vars.append(var)
                # Set the configuration if environment variable exists
                elif var.endswith("_CLIENT_ID"):
                    self.oauth_configs[platform]["client_id"] = os.getenv(var)
                elif var.endswith("_CLIENT_SECRET"):
                    self.oauth_configs[platform]["client_secret"] = os.getenv(var)

        if missing_vars:
            logger.warning(
                f"Missing OAuth environment variables: {', '.join(missing_vars)}. "
                f"OAuth flows for affected platforms will not work.",
            )

    async def initiate_oauth_flow(
        self,
        platform: str,
        user_id: str,
        redirect_uri: str,
    ) -> dict[str, Any]:
        """Initiate OAuth flow for a platform

        Args:
            platform: Platform name ('facebook', 'ebay', 'offerup', 'craigslist')
            user_id: User ID requesting authorization
            redirect_uri: URI to redirect after authorization

        Returns:
            Dict containing authorization URL and state

        """
        if platform not in self.oauth_configs:
            raise HTTPException(
                status_code=400,
                detail=f"Platform {platform} not supported",
            )

        config = self.oauth_configs[platform]

        # Handle platforms with OAuth
        if platform in ["facebook", "ebay"]:
            return await self._handle_oauth_platform(
                platform,
                user_id,
                redirect_uri,
                config,
            )

        # Handle platforms without OAuth (credential-based)
        if platform in ["offerup", "craigslist"]:
            return await self._handle_credential_platform(platform)

        raise HTTPException(
            status_code=400,
            detail=f"Integration method not implemented for {platform}",
        )

    async def _handle_oauth_platform(
        self,
        platform: str,
        user_id: str,
        redirect_uri: str,
        config: dict[str, Any],
    ) -> dict[str, Any]:
        """Handle OAuth-enabled platforms (Facebook, eBay)"""
        # Generate state parameter for security
        state = secrets.token_urlsafe(32)

        # Store state in database for verification
        await self.db.oauth_states.insert_one(
            {
                "state": state,
                "user_id": user_id,
                "platform": platform,
                "redirect_uri": redirect_uri,
                "created_at": datetime.utcnow(),
                "expires_at": datetime.utcnow() + timedelta(minutes=10),
            },
        )

        # Build authorization URL
        params = {
            "client_id": config["client_id"],
            "redirect_uri": redirect_uri,
            "scope": config["scope"],
            "response_type": "code",
            "state": state,
        }

        auth_url = f"{config['auth_url']}?{urlencode(params)}"

        return {
            "platform": platform,
            "auth_url": auth_url,
            "state": state,
            "method": "oauth",
            "instructions": f"Click the link to authorize {platform.title()} access",
        }

    async def _handle_credential_platform(self, platform: str) -> dict[str, Any]:
        """Handle credential-based platforms (OfferUp, Craigslist)"""
        platform_info = {
            "offerup": {
                "name": "OfferUp",
                "credentials_needed": ["email", "password"],
                "instructions": "Enter your OfferUp account credentials to enable posting",
                "security_note": "Credentials are encrypted and stored securely",
            },
            "craigslist": {
                "name": "Craigslist",
                "credentials_needed": ["email", "password"],
                "instructions": "Enter your Craigslist account credentials to enable posting",
                "security_note": "Credentials are encrypted and stored securely",
            },
        }

        info = platform_info[platform]

        return {
            "platform": platform,
            "method": "credentials",
            "credentials_needed": info["credentials_needed"],
            "instructions": info["instructions"],
            "security_note": info["security_note"],
            "form_url": f"/api/platforms/{platform}/credentials",
        }

    async def handle_oauth_callback(
        self,
        platform: str,
        code: str,
        state: str,
    ) -> dict[str, Any]:
        """Handle OAuth callback and exchange code for access token

        Args:
            platform: Platform name
            code: Authorization code from OAuth provider
            state: State parameter for verification

        Returns:
            Dict containing success status and account info

        """
        # Verify state parameter
        oauth_state = await self.db.oauth_states.find_one(
            {
                "state": state,
                "platform": platform,
                "expires_at": {"$gt": datetime.utcnow()},
            },
        )

        if not oauth_state:
            raise HTTPException(
                status_code=400,
                detail="Invalid or expired state parameter",
            )

        user_id = oauth_state["user_id"]
        config = self.oauth_configs[platform]

        try:
            # Exchange code for access token
            if platform == "facebook":
                token_data = await self._exchange_facebook_token(
                    code,
                    oauth_state["redirect_uri"],
                    config,
                )
            elif platform == "ebay":
                token_data = await self._exchange_ebay_token(
                    code,
                    oauth_state["redirect_uri"],
                    config,
                )
            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"OAuth not supported for {platform}",
                )

            # Store the token securely
            await self._store_platform_token(user_id, platform, token_data)

            # Clean up state
            await self.db.oauth_states.delete_one({"_id": oauth_state["_id"]})

            return {
                "success": True,
                "platform": platform,
                "user_id": user_id,
                "message": f"{platform.title()} account connected successfully",
            }

        except Exception as e:
            logger.exception(f"Error handling OAuth callback for {platform}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to connect {platform} account: {e!s}",
            ) from e

    async def _exchange_facebook_token(
        self,
        code: str,
        redirect_uri: str,
        config: dict,
    ) -> dict[str, Any]:
        """Exchange Facebook authorization code for access token"""
        params = {
            "client_id": config["client_id"],
            "client_secret": config["client_secret"],
            "redirect_uri": redirect_uri,
            "code": code,
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(config["token_url"], data=params)
            if response.status_code != 200:
                error_text = response.text
                raise Exception(f"Facebook token exchange failed: {error_text}")

            token_data = response.json()
            if not isinstance(token_data, dict):
                token_data = {}

            # Get user info
            user_info_url = f"{config['api_base']}/me?access_token={token_data.get('access_token', '')}&fields=id,name,email"
            user_response = await client.get(user_info_url)
            if user_response.status_code == 200:
                user_info = user_response.json()
                token_data["user_info"] = user_info

            return dict(token_data)

    async def _exchange_ebay_token(
        self,
        code: str,
        redirect_uri: str,
        config: dict,
    ) -> dict[str, Any]:
        """Exchange eBay authorization code for access token"""
        # eBay uses Basic Auth with client credentials
        auth_string = f"{config['client_id']}:{config['client_secret']}"
        auth_bytes = auth_string.encode("ascii")
        auth_b64 = base64.b64encode(auth_bytes).decode("ascii")

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {auth_b64}",
        }

        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    config["token_url"],
                    headers=headers,
                    data=data,
                    timeout=30.0,
                )

                if response.status_code == 200:
                    token_data = response.json()
                    return dict(token_data) if isinstance(token_data, dict) else {}

                # Handle specific eBay error responses
                try:
                    error_response = response.json()
                    error_code = error_response.get("error", "unknown_error")
                    error_description = error_response.get(
                        "error_description",
                        "Unknown error occurred",
                    )

                    # Sanitize and map eBay-specific errors to user-friendly messages
                    if error_code == "invalid_grant":
                        raise HTTPException(
                            status_code=400,
                            detail="Authorization code expired or invalid. Please try connecting again.",
                        )
                    if error_code == "invalid_client":
                        logger.error(
                            f"eBay OAuth client credentials invalid: {error_response}",
                        )
                        raise HTTPException(
                            status_code=500,
                            detail="eBay integration configuration error. Please contact support.",
                        )
                    if error_code == "unsupported_grant_type":
                        logger.error(f"eBay OAuth grant type error: {error_response}")
                        raise HTTPException(
                            status_code=500,
                            detail="eBay integration configuration error. Please contact support.",
                        )
                    if error_code == "invalid_scope":
                        logger.error(f"eBay OAuth scope error: {error_response}")
                        raise HTTPException(
                            status_code=400,
                            detail="Requested eBay permissions are not available. Please contact support.",
                        )
                    # Log full error for debugging but return sanitized message
                    logger.error(f"eBay token exchange error: {error_response}")
                    raise HTTPException(
                        status_code=400,
                        detail=f"eBay authorization failed: {error_description[:100]}",
                    )

                except (ValueError, KeyError):
                    # Response is not valid JSON or missing expected fields
                    logger.error(
                        f"eBay token exchange non-JSON error response: {response.status_code} - {response.text[:200]}",
                    )
                    if response.status_code == 400:
                        raise HTTPException(
                            status_code=400,
                            detail="Invalid authorization request. Please try connecting again.",
                        )
                    if response.status_code == 401:
                        raise HTTPException(
                            status_code=500,
                            detail="eBay integration authentication error. Please contact support.",
                        )
                    if response.status_code == 403:
                        raise HTTPException(
                            status_code=400,
                            detail="eBay access denied. Please check your account permissions.",
                        )
                    if response.status_code >= 500:
                        raise HTTPException(
                            status_code=503,
                            detail="eBay service temporarily unavailable. Please try again later.",
                        )
                    raise HTTPException(
                        status_code=400,
                        detail="eBay authorization failed. Please try again.",
                    )

            except httpx.TimeoutException:
                logger.error("eBay token exchange timeout")
                raise HTTPException(
                    status_code=503,
                    detail="eBay service timeout. Please try again.",
                )
            except httpx.RequestError as e:
                logger.error(f"eBay token exchange network error: {e!s}")
                raise HTTPException(
                    status_code=503,
                    detail="Network error connecting to eBay. Please try again.",
                )
            except HTTPException:
                # Re-raise our custom HTTP exceptions
                raise
            except Exception as e:
                logger.exception(
                    f"Unexpected error during eBay token exchange: {e!s}",
                )
                raise HTTPException(
                    status_code=500,
                    detail="Unexpected error during eBay authorization. Please try again.",
                )

    async def store_platform_credentials(
        self,
        user_id: str,
        platform: str,
        credentials: dict[str, str],
    ) -> dict[str, Any]:
        """Store platform credentials securely (for OfferUp, Craigslist)

        Args:
            user_id: User ID
            platform: Platform name
            credentials: Dict with platform credentials

        Returns:
            Success status

        """
        if platform not in ["offerup", "craigslist"]:
            raise HTTPException(
                status_code=400,
                detail=f"Credential storage not supported for {platform}",
            )

        try:
            # Encrypt credentials (you should implement proper encryption)
            encrypted_credentials = self._encrypt_credentials(credentials)

            # Store in database
            await self.db.platform_credentials.update_one(
                {"user_id": user_id, "platform": platform},
                {
                    "$set": {
                        "user_id": user_id,
                        "platform": platform,
                        "encrypted_credentials": encrypted_credentials,
                        "created_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow(),
                        "status": "active",
                    },
                },
                upsert=True,
            )

            return {
                "success": True,
                "platform": platform,
                "message": f"{platform.title()} credentials stored successfully",
            }

        except Exception as e:
            logger.exception(f"Error storing credentials for {platform}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to store {platform} credentials: {e!s}",
            ) from e

    async def _store_platform_token(
        self,
        user_id: str,
        platform: str,
        token_data: dict[str, Any],
    ) -> None:
        """Store OAuth token securely"""
        await self.db.platform_tokens.update_one(
            {"user_id": user_id, "platform": platform},
            {
                "$set": {
                    "user_id": user_id,
                    "platform": platform,
                    "access_token": token_data.get("access_token"),
                    "refresh_token": token_data.get("refresh_token"),
                    "token_type": token_data.get("token_type", "Bearer"),
                    "expires_in": token_data.get("expires_in"),
                    "scope": token_data.get("scope"),
                    "user_info": token_data.get("user_info", {}),
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow(),
                    "status": "active",
                },
            },
            upsert=True,
        )

    def _encrypt_credentials(self, credentials: dict[str, str]) -> str:
        """Encrypt credentials using Fernet symmetric encryption

        Args:
            credentials: Dictionary of credentials to encrypt

        Returns:
            Encrypted token string

        Raises:
            HTTPException: If encryption fails

        """
        try:
            # Convert credentials to JSON string
            credentials_json = json.dumps(credentials, sort_keys=True)
            credentials_bytes = credentials_json.encode("utf-8")

            # Encrypt using Fernet
            encrypted_token = self.cipher.encrypt(credentials_bytes)

            # Return as string (Fernet token is already base64 encoded)
            return encrypted_token.decode("utf-8")

        except Exception as e:
            logger.error(f"Failed to encrypt credentials: {e}")
            raise HTTPException(
                status_code=500,
                detail="Failed to secure credentials. Please try again.",
            ) from e

    def _decrypt_credentials(self, encrypted_token: str) -> dict[str, str]:
        """Decrypt credentials using Fernet symmetric encryption

        Args:
            encrypted_token: Encrypted token string

        Returns:
            Decrypted credentials dictionary

        Raises:
            HTTPException: If decryption fails

        """
        try:
            # Convert token string to bytes
            token_bytes = encrypted_token.encode("utf-8")

            # Decrypt using Fernet
            decrypted_bytes = self.cipher.decrypt(token_bytes)

            # Convert back to JSON and parse
            credentials_json = decrypted_bytes.decode("utf-8")
            credentials = json.loads(credentials_json)

            return dict(credentials) if isinstance(credentials, dict) else {}

        except InvalidToken as e:
            logger.exception(
                "Invalid token during decryption (token may be corrupted or encryption key changed)",
            )
            raise HTTPException(
                status_code=500,
                detail="Failed to retrieve stored credentials. Please reconnect your account.",
            ) from e
        except Exception as e:
            logger.error(f"Failed to decrypt credentials: {e}")
            raise HTTPException(
                status_code=500,
                detail="Failed to retrieve stored credentials. Please reconnect your account.",
            ) from e

    async def get_user_platforms(self, user_id: str) -> list[dict[str, Any]]:
        """Get all connected platforms for a user"""
        platforms: list[dict[str, Any]] = []

        # Get OAuth platforms
        oauth_platforms = await self.db.platform_tokens.find(
            {"user_id": user_id, "status": "active"},
        ).to_list(length=100)

        for platform in oauth_platforms:
            platforms.append(
                {
                    "platform": platform["platform"],
                    "type": "oauth",
                    "status": "connected",
                    "connected_at": platform["created_at"],
                    "user_info": platform.get("user_info", {}),
                },
            )

        # Get credential platforms
        cred_platforms = await self.db.platform_credentials.find(
            {"user_id": user_id, "status": "active"},
        ).to_list(length=100)

        for platform in cred_platforms:
            platforms.append(
                {
                    "platform": platform["platform"],
                    "type": "credentials",
                    "status": "connected",
                    "connected_at": platform["created_at"],
                },
            )

        return platforms

    async def disconnect_platform(self, user_id: str, platform: str) -> dict[str, Any]:
        """Disconnect a platform for a user"""
        try:
            # Remove OAuth tokens
            await self.db.platform_tokens.update_many(
                {"user_id": user_id, "platform": platform},
                {"$set": {"status": "disconnected", "updated_at": datetime.utcnow()}},
            )

            # Remove credentials
            await self.db.platform_credentials.update_many(
                {"user_id": user_id, "platform": platform},
                {"$set": {"status": "disconnected", "updated_at": datetime.utcnow()}},
            )

            return {
                "success": True,
                "platform": platform,
                "message": f"{platform.title()} disconnected successfully",
            }

        except Exception as e:
            logger.exception(f"Error disconnecting platform {platform}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to disconnect {platform}: {e!s}",
            ) from e
