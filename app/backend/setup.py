"""CrossPostMe Backend Setup"""

from setuptools import find_packages, setup

setup(
    name="crosspostme-backend",
    version="0.1.0",
    description="CrossPostMe Marketplace Automation Backend",
    packages=find_packages(exclude=["tests", "tests.*"]),
    python_requires=">=3.9",  # Python 3.8 is EOL, require 3.9+
    install_requires=[
        # Web framework and server
        "fastapi>=0.110.1,<1.0.0",  # Prevent breaking changes in 1.x
        "uvicorn>=0.25.0,<1.0.0",  # Prevent breaking changes in 1.x
        # Database drivers
        "motor>=3.3.1,<4.0.0",  # Async MongoDB driver
        "pymongo>=4.5.0,<5.0.0",  # MongoDB driver
        # Data validation and serialization
        "pydantic>=2.6.4,<3.0.0",  # Major version 2.x only
        # Environment and configuration
        "python-dotenv>=1.0.1,<2.0.0",  # Prevent breaking changes
        # Authentication and security
        "pyjwt>=2.10.1,<3.0.0",  # JWT handling
        "bcrypt>=4.1.3,<5.0.0",  # Password hashing
        "passlib>=1.7.4,<2.0.0",  # Password utilities
        "cryptography>=42.0.8,<43.0.0",  # Encryption (incremental releases)
        "python-jose>=3.3.0,<4.0.0",  # JOSE/JWT
        # HTTP client and utilities
        "httpx>=0.27.0,<1.0.0",  # Async HTTP client
        "python-multipart>=0.0.9,<1.0.0",  # Multipart form data
    ],
    extras_require={
        "dev": [
            "pytest>=8.0.0,<9.0.0",  # Testing framework
            "black>=24.1.1,<26.0.0",  # Code formatter
            "isort>=5.13.2,<6.0.0",  # Import sorter
            "flake8>=7.0.0,<8.0.0",  # Linter
            "mypy>=1.8.0,<2.0.0",  # Static type checker
        ],
    },
)
