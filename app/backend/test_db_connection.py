"""Database Connection Test Script - DEPRECATED
This file is deprecated. Please use the tests package instead.

Recommended usage:
  python -m tests.test_db_connection

Or with pytest:
  pytest tests/test_db_connection.py -v

This file is kept for backward compatibility only.
"""

import sys
from pathlib import Path

# Check if running from backend directory
backend_dir = Path(__file__).parent
if backend_dir.name == "backend":
    # Add backend to Python path for backward compatibility

    sys.path.insert(0, str(backend_dir))

    # Import and run the proper test (package-style import)
    from backend.tests.test_db_connection import main

    print("⚠️  WARNING: Using deprecated test file.")
    print("   Please use: python -m tests.test_db_connection")
    print("   Or: pytest tests/test_db_connection.py -v")
    print()

    if __name__ == "__main__":
        # Only execute when run as a script. This prevents pytest from importing
        # this legacy wrapper and executing tests during collection.
        main()
else:
    print("Error: This script must be run from the backend directory.")
    print("Recommended: python -m tests.test_db_connection")
    sys.exit(1)
