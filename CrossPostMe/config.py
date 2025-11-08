"""
Configuration loader for CrossPostMe application.
Handles environment-specific configuration and validates security settings.
"""

import logging
import os
import sys
from pathlib import Path
from typing import List

logger = logging.getLogger(__name__)


class ConfigError(Exception):
    """Raised when configuration validation fails."""

    pass


class Config:
    """Application configuration manager with environment-specific loading."""

    def __init__(self):
        self.node_env = os.getenv("NODE_ENV", "development")
        self._load_environment_config()
        self._validate_config()

    def _load_environment_config(self):
        """Load configuration from environment-specific .env file."""
        base_path = Path(__file__).parent

        # Determine which .env file to load
        if self.node_env == "production":
            env_file = base_path / ".env.production"
        elif self.node_env == "development":
            env_file = base_path / ".env.development"
        else:
            env_file = base_path / ".env"

        # Load environment file if it exists
        if env_file.exists():
            self._load_dotenv(env_file)
            logger.info(f"Loaded configuration from {env_file}")
        else:
            logger.warning(
                f"Environment file {env_file} not found, using system environment"
            )

    def _load_dotenv(self, file_path: Path):
        """Load environment variables from .env file."""
        try:
            with open(file_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        # Remove quotes if present
                        value = value.strip("\"'")
                        os.environ[key] = value
        except Exception as e:
            logger.error(f"Error loading {file_path}: {e}")

    def _validate_config(self):
        """Validate critical configuration settings."""
        # Validate CORS origins
        cors_origins = self.get_cors_origins()
        if not cors_origins:
            raise ConfigError("CORS_ORIGINS environment variable is required")

        if "*" in cors_origins and self.node_env == "production":
            raise ConfigError(
                "CORS_ORIGINS cannot contain wildcard '*' in production environment. "
                "Please specify allowed origins explicitly."
            )

        # Validate required secrets in production
        if self.node_env == "production":
            required_secrets = [
                "SECRET_KEY",
                "JWT_SECRET_KEY",
                "CREDENTIAL_ENCRYPTION_KEY",
            ]
            for secret in required_secrets:
                value = os.getenv(secret)
                if not value or value.startswith("dev_"):
                    raise ConfigError(
                        f"{secret} must be set to a secure value in production "
                        "(not a development placeholder)"
                    )

    def get_cors_origins(self) -> List[str]:
        """Get validated CORS origins as a list."""
        origins_str = os.getenv("CORS_ORIGINS", "")
        if not origins_str:
            return []

        # Split by comma and clean whitespace
        origins = [
            origin.strip() for origin in origins_str.split(",") if origin.strip()
        ]
        return origins

    def get_mongo_url(self) -> str:
        """Get MongoDB connection URL."""
        return os.getenv("MONGO_URL", "mongodb://localhost:27017")

    def get_db_name(self) -> str:
        """Get database name."""
        return os.getenv("DB_NAME", "crosspostme_dev")

    def get_secret_key(self) -> str:
        """Get application secret key."""
        return os.getenv("SECRET_KEY", "fallback-secret-change-in-production")

    def get_jwt_secret_key(self) -> str:
        """Get JWT secret key."""
        return os.getenv("JWT_SECRET_KEY", "fallback-jwt-secret-change-in-production")

    def get_credential_encryption_key(self) -> str:
        """Get credential encryption key."""
        return os.getenv(
            "CREDENTIAL_ENCRYPTION_KEY", "fallback-cred-key-change-in-production"
        )

    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.node_env == "production"

    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.node_env == "development"


# Global configuration instance
config = Config()

# Platform configurations
AVAILABLE_PLATFORMS = [
    {"name": "facebook", "enabled": True},
    {"name": "craigslist", "enabled": True},
    {"name": "offerup", "enabled": True},
    {"name": "ebay", "enabled": True},
]


def validate_startup_config():
    """Validate configuration at application startup."""
    try:
        # This will trigger validation
        config._validate_config()

        logger.info(f"Configuration validated for {config.node_env} environment")
        logger.info(f"CORS origins: {config.get_cors_origins()}")
        logger.info(f"Database: {config.get_db_name()}")

    except ConfigError as e:
        logger.error(f"Configuration validation failed: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error during configuration validation: {e}")
        sys.exit(1)
