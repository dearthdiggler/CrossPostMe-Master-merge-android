<!--
High-level, actionable Copilot instructions describing the integrations used in this repository
and the runtime/deployment process. Intended as a short, precise reference for AI coding
agents and contributors to understand what systems connect to what and how CI/deploy works.
-->

# Integrations & Process (for Copilot & contributors)

This document lists all external systems and integrations the project uses, and explains the
typical developer, CI, and deployment flows so an AI agent or contributor can make safe
changes and create new automation.

Keep this file short and actionable. If you change a deployment flow or add/remove an
integration, update this file.

---

## Quick map

- Frontend: `app/frontend` — Create React App (CRACO), Tailwind, shadcn/ui, dev server runs on 3000.
- Backend: `app/backend` — FastAPI, uvicorn, Motor (async Mongo client), Python dependencies in `requirements.txt` / `pyproject.toml`.
- Database: MongoDB Atlas (managed). App connects using `MONGO_URL` and `DB_NAME` environment variables.
- Hosting: Frontend static files → Hostinger (FTP/SFTP or SSH deploy). Backend → Render.com (recommended) or other hosting (Railway, VPS).
- CI/CD: GitHub Actions workflows in `.github/workflows`:
  - Frontend Hostinger deploy (tarball + scp) — `deploy-hostinger-scp.yml` (or original FTP workflow).
  - Playground deploy to `public/playground/` on Hostinger — `deploy-hostinger-playground.yml`.
  - Mongo connectivity test (environment-level secret) — `check-mongo-connection.yml`.
- SSH keys: private key(s) are stored in local `~/.ssh/crosspostme_deploy` and referenced in Actions as environment secrets (e.g., `HOSTINGER_SSH_KEY`).
- Diagram utility: mermaid diagrams used in docs — keep diagrams in docs or markdown where helpful.

## Secrets & environment

- Secrets are stored in GitHub Actions (either repo-level or environment `CrossEnv`). Keys of interest:
  - `HOSTINGER_SSH_KEY`, `HOSTINGER_SSH_USER`, `HOSTINGER_SSH_HOST`, `HOSTINGER_SSH_PORT`
  - `MONGO_URL`, `DB_NAME` (Atlas connection string and DB name)
  - Any API keys for third-party services (Google, etc.).
- Never commit secrets; use GH Actions secrets or the host's environment settings (Render environment variables).

## Dev flow (local)

1. Backend:
   - Create & activate a virtualenv in `app/backend` (the repo contains notes and `requirements.txt`).
   - Install deps: `pip install -r requirements.txt` (or `pip install -e .` if using pyproject).
   - Run dev server: `uvicorn server:app --reload --app-dir app/backend --port 8000` (or use the provided start scripts).
   - The backend reads `MONGO_URL`/`DB_NAME` from environment or `.env` (do not commit `.env`).
2. Frontend:
   - `cd app/frontend && yarn install && yarn start` (CRACO dev server runs on 3000). Use `HOST=127.0.0.1 PORT=3000` if necessary.

## CI / Deploy flow (what the workflows do)

- Frontend deploy (Hostinger):
  1. Checkout code.
  2. Build frontend (`npm ci && npm run build`).
  3. Create a tarball of `app/frontend/build`.
  4. Use SSH private key (from `HOSTINGER_SSH_KEY`) to `scp` the tarball to `/tmp/` on Hostinger.
  5. SSH into the server and extract into `public/` (production) or `public/playground/` (playground branch).
- Backend (Render):
  - Render usually auto-deploys from the GitHub repo when you connect the service.
  - Add required env vars in Render dashboard: `MONGO_URL`, `DB_NAME`, `SECRET_KEY`, `CORS_ORIGINS`.
  - If you run into TLS/SSL issues when connecting to Atlas from Render, use the `certifi` CA bundle and pass `tlsCAFile=certifi.where()` to the Mongo client (code examples are in repo docs).

## MongoDB Atlas specifics

- Atlas connection string must have the password URL-encoded per RFC 3986 (use `urllib.parse.quote_plus` or PowerShell `EscapeDataString`).
- Atlas restricts inbound IPs. Add Render outbound IPs or your own host IPs in Atlas Network Access, or use `0.0.0.0/0` temporarily for testing then tighten.
- There are separate Atlas API keys (public/private) used for automation — those are management API credentials, not DB credentials. Store them separately if used.

## Code changes required for Render TLS issues (already applied/needed)

- Add `certifi` to Python dependencies.
- When constructing Motor/PyMongo clients, pass the CA bundle explicitly (example):

```python
from certifi import where
client = AsyncIOMotorClient(MONGO_URL, tls=True, tlsCAFile=where())
```

This avoids TLS handshake issues on some PaaS platforms.

## Playgrounds & staging

- The `playground` branch deploys to `public/playground/` on Hostinger and can be served from `playground.yourdomain.com` when a subdomain points to that path.
- Use this for UI experiments — keep it isolated from production root.

## Mermaids (diagrams)

- Mermaid diagrams are embedded in markdown docs. If you regenerate diagrams or add flow charts, commit the markdown and, if used in docs site, ensure the viewer supports mermaid rendering.

## Where Mongo client is defined (so Copilot knows what to change)

- Primary client is constructed in `app/backend/db.py` in a class that wraps `AsyncIOMotorClient`.
- Other places creating clients: `app/backend/scripts/setup_db.py`, `app/backend/automation/credentials.py`, `app/backend/scripts/check_mongo.py` (test helper). Update constructors there as well.

## Health checks and tests

- The backend exposes `/api/status` and `/api/health` endpoints — CI or deploy scripts should probe those after deploy.
- A GH Actions job `check-mongo-connection.yml` exists to test Atlas connectivity using secrets in `CrossEnv`.

## Troubleshooting checklist (fast)

1. If frontend refuses to connect locally: ensure CRA bound to 127.0.0.1 and port 3000 is available.
2. If Mongo driver throws username/password errors: URL-encode password.
3. If Atlas rejects connection: check IP allowlist.
4. If Render TLS errors: add `certifi` and pass `tlsCAFile=certifi.where()` in client constructor.

## Safe edit rules for AI agents

- Never print secrets or persist them in files.
- When editing deploy workflows, preserve existing secret names and environment declaration `CrossEnv` unless intentionally changing them. Add new secrets only as placeholders and document them.
- When changing DB client options, add a short comment referencing `certifi` and the reason for the explicit CA file.
- If adding new dependencies, update `requirements.txt` or `pyproject.toml` and run basic static checks (import tests) where possible.

---

Last updated: please update this file whenever you change hosting, CI, or DB patterns.
