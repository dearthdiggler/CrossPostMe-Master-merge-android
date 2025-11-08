#!/usr/bin/env python3
"""Simple MongoDB connectivity checker.
Reads MONGO_URL from the environment and attempts a server_info() call.
Prints a short success/failure message and up to 10 database names (non-sensitive).
"""
import os
import sys

import certifi
from pymongo import MongoClient


def main():
    uri = os.environ.get("MONGO_URL")
    if not uri:
        print("MONGO_URL environment variable is not set", file=sys.stderr)
        sys.exit(2)
    try:
        # Use certifi bundle for TLS when connecting to Atlas (mongodb+srv)
        client_opts = {"serverSelectionTimeoutMS": 5000}
        if uri.startswith("mongodb+srv") or "mongodb+srv" in uri:
            client_opts.update({"tls": True, "tlsCAFile": certifi.where()})
        client = MongoClient(uri, **client_opts)
        info = client.server_info()
        print("Connected to MongoDB version", info.get("version"))
        dbs = client.list_database_names()
        print("Databases (up to 10):", dbs[:10])
        client.close()
        sys.exit(0)
    except Exception as e:
        print("Connection failed:", e, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
