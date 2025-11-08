Environment variables and GitHub Secrets (backend)

This file documents the environment variables and GitHub Actions secrets the backend expects and the new secrets you've added in GitHub Actions (example names shown).

IMPORTANT: Do NOT commit credentials or private keys into source control. Use GitHub Actions secrets (repo or environment-level) or the host's environment variables.

Required runtime env vars (for the backend process)

- MONGO_URL (required) - the full MongoDB connection string used by the application. Example (Atlas SRV):
  - mongodb+srv://DBUSER:DBPASS@CLUSTER.mongodb.net/DBNAME?retryWrites=true&w=majority
  - Set this value as a GitHub secret (environment CrossEnv or repository secret) named MONGO_URL if your deployment needs it.
- DB_NAME (required) - the database name (for example: marketwiz).
- SECRET_KEY (recommended) - application secret used for signing tokens.
- CORS_ORIGINS (recommended) - comma-separated origins allowed for CORS (for example: https://yourfrontend.example)

GitHub secrets you mentioned

- MONGO_SHARDNAME - the cluster or shard name (Atlas cluster name). Useful for automation scripts.
- MONGODB_PUBLICKEY / MONGODB_PRIVATEKEY - typically MongoDB Atlas API keys (Public Key / Private Key) used for programmatic access to Atlas management APIs. These are not the DB username/password pair used in MONGO_URL.

How to create a runtime DB connection string

1. Create a database user in MongoDB Atlas (Database Access -> Add New Database User). Choose a username and password.
2. Get the connection string from Cluster -> Connect -> Connect your application, and replace the placeholders with the DB username and password and database name.
3. Store the full connection string as the secret MONGO_URL and set DB_NAME to the database name.

Commands (GitHub CLI) to set secrets into the environment CrossEnv

Note: adjust values before running. These commands require the GitHub CLI (gh) and appropriate permissions.

gh secret set MONGO_URL -e CrossEnv --body "mongodb+srv://DBUSER:DBPASS@CLUSTER.mongodb.net/DBNAME?retryWrites=true&w=majority"
gh secret set DB_NAME -e CrossEnv --body "marketwiz"

If you currently only have MONGODB_PUBLICKEY and MONGODB_PRIVATEKEY and MONGO_SHARDNAME, those are Atlas management API keys and the cluster name. They are not the DB credentials. Use the Atlas UI or API to create a DB user for the application.

Quick steps (Atlas UI)

1. Log into MongoDB Atlas.
2. Create a database user (Database Access -> Add New Database User) with a username and password.
3. Obtain the connection string from Cluster -> Connect -> Connect your application and substitute the username and password.
4. Add that string to GitHub Secrets as MONGO_URL (or environment secret if you prefer environment-level secrets).

Optional next additions I can make

- Add placeholders in CI workflow referring to secrets MONGO_URL and DB_NAME so deploys or health checks can use them.
- Add a small local script scripts/check_mongo.py that attempts a connection using MONGO_URL for CI health checks.

Tell me which (if any) of the optional items you want me to add.
