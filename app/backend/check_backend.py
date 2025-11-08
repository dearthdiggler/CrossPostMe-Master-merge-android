import asyncio
import sys
from pathlib import Path

# Ensure parent directory is on sys.path so the top-level 'backend' package
# can be imported when running this script from inside the package folder.
repo_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(repo_root))

print("importing backend.server...")
try:
    print("imported backend.server OK")
except Exception as e:
    print("import error:", type(e).__name__, e)
    # continue to try DB ping even if import fails

print("\nchecking DB connection...")
try:
    from backend.db import get_typed_db

    db = get_typed_db()
    ok = asyncio.run(db.validate_connection())
    print("db.validate_connection() ->", ok)
except Exception as e:
    print("db validate error:", type(e).__name__, e)
    sys.exit(1)
