# Authoritative, concise guidance for AI agents working in this repo

## Copilot instructions (canonical)

Repository layout (high signal):

- `backend/` — FastAPI backend (entry: `server.py`, routes: `routes/`, models: `models.py`). Uses Motor (async MongoDB).
- `frontend/` — Create React App with CRACO, Tailwind and shadcn/ui (entry: `package.json`, config: `craco.config.js`).

Quick checks to run first:

- open `backend/server.py` to inspect mounted routers, DB client lifecycle, and environment var usage (`MONGO_URL`, `DB_NAME`, `CORS_ORIGINS`).
- open `backend/routes/*` to copy router patterns (each route file exports `router = APIRouter(...)`).
- open `frontend/package.json` and `craco.config.js` for dev/start/build commands and aliases.

Project conventions you must follow:

- Routes: export an `APIRouter` in `backend/routes/*.py` and include it in `server.py` via `app.include_router(...)`.
- DB: prefer reusing the shared Motor client created in `server.py`. Hunt for local `get_db()` functions that create new clients and avoid duplicating clients.
- Data: datetimes are serialized as ISO strings before inserts; Pydantic models often set `model_config = ConfigDict(extra="ignore")` to ignore MongoDB `_id`.
- Query pattern: many handlers use `.to_list(1000)` and then map results to Pydantic models — follow this pattern for lists/pagination.

Short dev commands (PowerShell):

```powershell
# Backend
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r app/backend/requirements.txt
uvicorn server:app --reload --app-dir app/backend

# Frontend
cd app/frontend
yarn install
yarn start
```

Tests & quality tools:

- Backend: `pytest`, formatting with `black .`, linters available in `app/backend/requirements.txt` (flake8, mypy).
- Frontend: CRA test runner (`yarn test`), ESLint via devDependencies.

Deployment & infra:

- Dockerfiles (`Dockerfile.backend`, `Dockerfile.frontend`) and `docker-compose.yml` are provided for containerized runs.
- Backend loads `.env` via `dotenv` in `server.py`. Do not commit secrets.

Where to look for concrete examples:

- `backend/routes/ads.py`, `platforms.py`, `ai.py` — router + DB usage examples
- `backend/server.py` — app entry, CORS setup, DB client lifecycle
- `frontend/package.json`, `craco.config.js`, `src/` — frontend structure and components

If you add CI: create `.github/workflows/` entries that run `pip install -r backend/requirements.txt && pytest` and `cd frontend && yarn install && yarn test --ci`.

If something is unclear (deployment target, DB credentials, CI expectations), stop and ask a maintainer — include which manifests you inspected and a short plan for the change.
