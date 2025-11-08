"""Small utility to create or update an admin user in MongoDB.

Usage (local):
  python create_admin.py --email admin@example.com --username admin --password secret

Notes:
 - This script hashes the password before storing it and will not print the password.
 - Do NOT commit plaintext passwords. Use environment variables or prompts in CI.

"""

import argparse
import asyncio
import os
import sys
from pathlib import Path
from typing import Any

# ruff: noqa: E402
# Ensure the project root is on sys.path when running this script directly
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import getpass
import uuid

from backend.auth import get_password_hash
from backend.db import get_typed_db
from pymongo.errors import PyMongoError


async def main(args: argparse.Namespace) -> None:
    db: Any = get_typed_db()
    # Find existing user by email (protected)
    try:
        existing = await db.users.find_one({"email": args.email})
    except PyMongoError as e:
        import sys
        import traceback

        print(f"Error: failed to query users collection: {e!s}", file=sys.stderr)
        traceback.print_exc()
        sys.exit(1)
    except Exception:
        # Unexpected non-database error - re-raise after logging for developer visibility
        import sys
        import traceback

        print("Unexpected error while querying users collection", file=sys.stderr)
        traceback.print_exc()
        raise

    password = args.password
    if args.prompt:
        password = getpass.getpass(prompt="Enter password for admin (input hidden): ")

    if not password:
        print("Error: password is required")
        return

    user_doc = {
        "id": existing["id"] if existing else str(uuid.uuid4()),
        "username": args.username,
        "email": args.email,
        "hashed_password": get_password_hash(password),
        "is_active": True,
        "is_admin": True,
    }

    try:
        if existing:
            # If not forced, prompt interactively to avoid accidental overwrite
            force = getattr(args, "yes", False)
            if not force:
                prompt = (
                    input(
                        f"Admin user for {args.email} already exists. Overwrite username and password?\n"
                        "This will replace the following fields: username, hashed_password, is_active, is_admin.\n"
                        "Type 'y' or 'yes' to confirm: ",
                    )
                    .strip()
                    .lower()
                )
                if prompt not in ("y", "yes"):
                    print("Aborted: existing admin user was not modified.")
                    return

            await db.users.update_one({"email": args.email}, {"$set": user_doc})
            print(f"Updated admin user for {args.email}")
        else:
            await db.users.insert_one(user_doc)
            print(f"Created admin user for {args.email}")
    except PyMongoError as e:
        import sys
        import traceback

        print(f"Error: failed to write admin user to database: {e!s}", file=sys.stderr)
        traceback.print_exc()
        sys.exit(1)
    except Exception:
        # Unexpected non-database error - re-raise after logging for developer visibility
        import sys
        import traceback

        print("Unexpected error while writing admin user to database", file=sys.stderr)
        traceback.print_exc()
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--email", required=True)
    parser.add_argument("--username", required=True)
    parser.add_argument("--password", required=False)
    parser.add_argument(
        "--prompt",
        action="store_true",
        help="Prompt for password interactively",
    )
    parser.add_argument(
        "-y",
        "--yes",
        "--force",
        action="store_true",
        help="Non-interactive: overwrite existing admin without prompting",
    )

    args = parser.parse_args()

    # Run the creation (password will be prompted if --prompt is provided)
    # Support environment override for automation: ADMIN_CREATE_FORCE=true
    env_force = os.getenv("ADMIN_CREATE_FORCE", "false").lower() in ("1", "true", "yes")
    # If environment forces, set args.yes so main() can rely on it
    if env_force and not getattr(args, "yes", False):
        args.yes = True

    asyncio.run(main(args))
