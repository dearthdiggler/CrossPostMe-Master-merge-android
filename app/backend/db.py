import logging
import os
import ssl
import warnings
from pathlib import Path
from typing import Any

import certifi
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

# Load environment variables
load_dotenv(Path(__file__).parent / ".env")


class Database:
    """MongoDB Database wrapper with async Motor client.

    This class provides typed access to MongoDB collections and handles
    TLS configuration, connection timeouts, and security settings.

    IMPORTANT: After instantiation, call await instance.validate_connection()
    to ensure the database is reachable and the connection is valid.
    This enables early detection of invalid URLs or unreachable servers.

    Example:
        db = Database(mongo_url, db_name)
        is_connected = await db.validate_connection()
        if not is_connected:
            # Handle connection failure
            raise Exception("Failed to connect to MongoDB")

    """

    def __init__(self, mongo_url: str, db_name: str):
        """Initialize MongoDB client with intelligent TLS and timeout configuration.

        Args:
            mongo_url: MongoDB connection string (mongodb:// or mongodb+srv://)
            db_name: Database name to use

        Note:
            Connection is not validated during initialization. Call
            await validate_connection() after instantiation to verify connectivity.

        """
        # Determine TLS settings based on connection string and environment
        # Precedence: MONGO_TLS_OVERRIDE env var > connection string inference

        # Check for explicit TLS override from environment
        tls_override = os.getenv("MONGO_TLS_OVERRIDE")

        if tls_override is not None:
            # Explicit override takes precedence
            use_tls = tls_override.lower() in ("true", "1", "yes")
        else:
            # Infer from connection string
            # Local development: localhost, 127.0.0.1, or plain mongodb:// protocol
            is_local = any(
                [
                    "localhost" in mongo_url.lower(),
                    "127.0.0.1" in mongo_url,
                    mongo_url.startswith("mongodb://")
                    and not mongo_url.startswith("mongodb+srv://"),
                ],
            )
            # MongoDB Atlas uses mongodb+srv:// which requires TLS
            use_tls = not is_local

        # Configure server selection timeout (in milliseconds)
        # Configurable via environment variable for tuning without code changes
        # Default: 15000ms (15 seconds) - suitable for cold starts and slow networks
        # Can be lowered for faster failure detection in stable environments
        server_selection_timeout = int(
            os.getenv("MONGO_SERVER_SELECTION_TIMEOUT_MS", "15000"),
        )

        # Build client options
        client_options: dict[str, Any] = {
            "serverSelectionTimeoutMS": server_selection_timeout,
        }

        # Add TLS options only when TLS is enabled
        if use_tls:
            client_options["tls"] = True

            # Use certifi's certificate bundle for reliable SSL/TLS connections
            # This ensures compatibility across different Python versions and platforms
            # Prefer the modern 'tls*' options only to avoid conflicts with legacy
            # 'ssl_*' options which can override behavior (tlsAllowInvalidCertificates etc.).
            client_options["tlsCAFile"] = certifi.where()

            # Diagnostic logging to help with TLS handshake issues in hosted envs
            logger = logging.getLogger(__name__)
            openssl_version = getattr(ssl, "OPENSSL_VERSION", "unknown")
            logger.info(
                "MongoDB TLS enabled. tlsCAFile=%s, OpenSSL=%s",
                certifi.where(),
                openssl_version,
            )

            # Certificate validation protection for sensitive environments
            # Only allow invalid certificates in explicitly safe development/test environments
            env_name = os.getenv(
                "ENV",
                os.getenv("FLASK_ENV", os.getenv("ENVIRONMENT", "development")),
            ).lower()

            # Safe environments where certificate validation can be disabled for testing
            safe_environments = {"development", "dev", "local", "test"}
            is_safe_environment = env_name in safe_environments

            # Check if invalid certificates are requested
            allow_invalid_certs_env = (
                os.getenv("MONGO_TLS_ALLOW_INVALID_CERTS", "false").lower() == "true"
            )
            testing_override = (
                os.getenv("ALLOW_INVALID_CERTS_FOR_TESTING", "false").lower() == "true"
            )

            if allow_invalid_certs_env or testing_override:
                # CRITICAL: Only allow invalid certificates in safe development/test environments
                if not is_safe_environment:
                    error_parts = [
                        "SECURITY ERROR: Attempted to disable TLS certificate validation in non-development environment.",
                        f"Environment detected as: {env_name}.",
                        (
                            "Only safe environments are allowed: "
                            f"{', '.join(sorted(safe_environments))}."
                        ),
                        "Invalid certificate settings:",
                        f"MONGO_TLS_ALLOW_INVALID_CERTS={allow_invalid_certs_env},",
                        f"ALLOW_INVALID_CERTS_FOR_TESTING={testing_override}.",
                        "This is forbidden for security reasons.",
                        (
                            "Remove these environment variables or set ENV to one of: "
                            f"{', '.join(sorted(safe_environments))}."
                        ),
                    ]
                    error_msg = " ".join(error_parts)
                    raise RuntimeError(error_msg)

                # Allow invalid certs only in safe development/test environments
                # Both MONGO_TLS_ALLOW_INVALID_CERTS and ALLOW_INVALID_CERTS_FOR_TESTING are honored
                warn_parts = [
                    f"WARNING: TLS certificate validation disabled in {env_name} environment.",
                    f"MONGO_TLS_ALLOW_INVALID_CERTS={allow_invalid_certs_env},",
                    f"ALLOW_INVALID_CERTS_FOR_TESTING={testing_override}.",
                    "This should ONLY be used in development/test environments!",
                ]
                warnings.warn(" ".join(warn_parts), UserWarning, stacklevel=2)
                client_options["tlsAllowInvalidCertificates"] = True

        # Motor's AsyncIOMotorClient stubs can produce spurious mypy errors
        # (they're runtime factories in some versions). Use Any for the
        # runtime client to avoid false positives while preserving behavior.
        self._client: Any = AsyncIOMotorClient(
            mongo_url,
            **client_options,  # type: ignore[arg-type]
        )
        # Underlying Motor database is dynamically typed; annotate as Any
        self._db: Any = self._client[db_name]

        # Expose commonly used collections with typing
        # Motor collections are dynamically typed; annotate as Any for simplicity
        self.users: Any = self._db.users
        self.ads: Any = self._db.ads
        self.posted_ads: Any = self._db.posted_ads
        self.platform_accounts: Any = self._db.platform_accounts
        self.status_checks: Any = self._db.status_checks

        # OAuth and Platform Integration collections
        self.platform_tokens: Any = self._db.platform_tokens
        self.platform_credentials: Any = self._db.platform_credentials
        self.oauth_states: Any = self._db.oauth_states

        # Message and Lead Management collections
        self.messages: Any = self._db.messages
        self.leads: Any = self._db.leads
        self.response_templates: Any = self._db.response_templates
        self.outgoing_responses: Any = self._db.outgoing_responses
        self.monitoring_configs: Any = self._db.monitoring_configs
        self.email_rules: Any = self._db.email_rules

        # Additional collections used by routes
        self.diagrams: Any = self._db.diagrams

        # Payment and Subscription collections (used by stripe_payments.py)
        self.payments: Any = self._db.payments
        self.subscriptions: Any = self._db.subscriptions

    async def validate_connection(self) -> bool:
        """Validate the MongoDB connection by pinging the server.

        This method should be called after instantiation to verify that the
        database is reachable and the connection configuration is valid.
        Useful for early detection of invalid URLs, authentication failures,
        or unreachable servers.

        Returns:
            bool: True if connection is valid and server responds to ping,
                  False if connection fails for any reason.

        Raises:
            None - All exceptions are caught and a warning is emitted.

        Example:
            db = Database(mongo_url, db_name)
            if await db.validate_connection():
                print("Database connection successful")
            else:
                print("Database connection failed - check logs")

        """
        try:
            # Ping the MongoDB server to validate connection
            await self._client.admin.command("ping")
        except Exception as e:
            # Emit warning with error details for debugging
            # Include SSL-specific context when available to aid diagnostics
            # Build SSL diagnostic info using safe attribute access
            openssl_version = getattr(ssl, "OPENSSL_VERSION", "unknown")
            # certifi is imported above; directly call certifi.where().
            # Use a simple fallback in case of unexpected errors.
            try:
                certifi_where = certifi.where()
            except Exception:
                certifi_where = "unknown"

            ssl_info = {
                "openssl_version": openssl_version,
                "certifi_where": certifi_where,
            }

            error_parts = [
                f"MongoDB connection validation failed: {type(e).__name__}: {e!s}.",
                f"SSL info: {ssl_info}.",
                (
                    "Please check your MONGO_URL, network connectivity, "
                    "and MongoDB server status."
                ),
            ]
            warnings.warn(" ".join(error_parts), UserWarning, stacklevel=2)
            return False
        else:
            # Connection successful - only executed when no exception occurred
            return True

    def get_collection(self, name: str) -> Any:
        """Get a collection by name for dynamic access"""
        return self._db[name]

    def __getitem__(self, name: str) -> Any:
        """Allow index-style access db['collection'] for convenience and typing.

        Returns Any because Motor collections are dynamically typed at runtime.
        """
        return self.get_collection(name)

    def close(self):
        """Close the MongoDB client connection"""
        if self._client:
            self._client.close()

    def disconnect(self):
        """Alias for close() to ensure all async connections are closed"""
        self.close()


_database: Database | None = None


def get_db() -> Database:
    global _database
    if _database is None:
        mongo_url = os.environ.get("MONGO_URL")
        db_name = os.environ.get("DB_NAME")

        # Development fallbacks
        if not mongo_url:
            warnings.warn(
                "MONGO_URL not set, using development fallback",
                UserWarning,
                stacklevel=2,
            )
            mongo_url = "mongodb://localhost:27017"

        if not db_name:
            warnings.warn(
                "DB_NAME not set, using development fallback",
                UserWarning,
                stacklevel=2,
            )
            db_name = "crosspostme"

        _database = Database(mongo_url, db_name)
    return _database


def get_typed_db() -> Database:
    """Get the typed database instance for use in server.py and routes"""
    return get_db()
