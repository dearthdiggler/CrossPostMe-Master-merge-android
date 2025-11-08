````instructions
<!--
This file is a backup of the original `.github/copilot-instructions.md` prior to replacement.
It preserves the longer, auto-generated guidance and examples for future reference.
-->

# Copilot instructions for contributors and AI agents


Repository snapshot (discoverable):
- Top-level working folder: `app/` with two main subprojects: `backend/` (FastAPI) and `frontend/` (Create React App + craco).

Quick start checklist (what I do first):
1. List `app/` to confirm files and manifests. Example (PowerShell):
   ```powershell
   Get-ChildItem -Path .\app -Force -Recurse -Depth 2
   ```
2. Auto-detect stack by looking at these files (already present here):
   - `backend/requirements.txt` -> Python FastAPI stack (FastAPI, uvicorn, motor, pydantic, pytest, linters)
   - `backend/server.py` -> Entrypoint for backend API, includes routers from `backend/routes/`
   - `frontend/package.json` -> Frontend is Create React App (uses `craco`); scripts: `start`, `build`, `test`.

Big-picture architecture (what to know):
- Backend: FastAPI application implemented in `backend/server.py`. It uses `motor` (async MongoDB client) and expects env vars `MONGO_URL` and `DB_NAME`. Route modules live in `backend/routes/` (examples: `ads.py`, `platforms.py`, `ai.py`) and export `router` objects that are included via `app.include_router(...)`.
- Frontend: Create React App augmented with `craco` in `frontend/`. The app uses React 19, Tailwind and numerous Radix UI packages. Start/build/test are driven by `craco` (see `frontend/package.json`).
- Data flow: backend persists data into MongoDB via Motor. Timestamps are serialized as ISO strings before inserting into MongoDB (see `server.py`), and route handlers commonly exclude MongoDB's `_id` or ignore it via Pydantic `ConfigDict(extra="ignore")`.

Key files to inspect (high signal):
- `backend/server.py` — main app, router mounting, CORS config, DB client lifecycle, example endpoints (`/api/status`)
- `backend/routes/*.py` — route modules that must export a `router` variable
- `backend/requirements.txt` — pinned deps and dev tools (pytest, black, isort, flake8, mypy)
- `frontend/package.json` — start/build/test scripts; dependency list and package manager (yarn v1)
- `frontend/src/` — React components and pages (UI lives under `frontend/src/components` and `frontend/src/pages`)

Concrete route patterns (examples from `backend/routes/`):
- Each route module defines an `APIRouter` with a `prefix` and registers endpoints. Example: `ads.py` uses `router = APIRouter(prefix="/api/ads", tags=["ads"])` and exports `router`.
- Database pattern: route modules call a local `get_db()` which creates an `AsyncIOMotorClient` from `MONGO_URL` and selects `DB_NAME`. Example usage: `db = get_db()` then `await db.ads.find({...}).to_list(1000)` or `await db.ads.insert_one(obj.dict())`.
- Error handling: endpoints raise `HTTPException` for 404s (e.g., ad/account not found).
- Route examples you can use when adding new routes:
  - Create resource: `@router.post('/', response_model=Model)` -> insert and return pydantic model
  - Read list: `@router.get('/', response_model=List[Model])` -> `await db.collection.find(query).to_list(1000)` then map to models
  - Read single: `@router.get('/{id}')` -> `await db.collection.find_one({'id': id})` else raise 404
  - Update: `await db.collection.update_one({'id': id}, {'$set': update_data})` then return updated document

Async & DB gotchas
- Motor client creation is cheap but clients should be closed on shutdown. `server.py` creates a client at top-level and closes on shutdown; route modules sometimes create their own client via `get_db()` — prefer reusing the main client when possible to avoid extra connections.
- When inserting documents, timestamps are converted to ISO strings before insert; when reading, endpoints convert ISO back to `datetime`.

If you add or modify route modules:
- Export a `router` APIRouter and include it in `backend/server.py` with `app.include_router(your_module.router)`.
- Add Pydantic models in `backend/models.py` and use `ConfigDict(extra='ignore')` when you want to safely ignore MongoDB `_id`.


Environment & secrets (how this repo expects secrets):
- Backend reads environment variables (loaded from a `.env` via `dotenv` in `server.py`). Required keys (look for usages in `server.py` and routes): `MONGO_URL`, `DB_NAME`, `CORS_ORIGINS`.
- Do not commit secrets. Use `.env` locally and document required vars in `README.md` when you add them.

Developer workflows (concrete commands)
- Backend (PowerShell):
  ```powershell
  # create venv, install, run dev server
  python -m venv .venv; .\.venv\Scripts\Activate.ps1
  pip install -r .\app\backend\requirements.txt
  # set .env or environment variables, then:
  uvicorn server:app --reload --host 0.0.0.0 --port 8000 --app-dir .\app\backend
  ```
- Frontend (PowerShell, uses yarn v1 as packageManager):
  ```powershell
  cd .\app\frontend
  yarn install
  yarn start
  # build for production
  yarn build
  ```

Project-specific conventions and gotchas
- Route modules must expose a `router` FastAPI APIRouter and be included in `server.py` via `app.include_router(...)` — check `backend/routes/ads.py` and `platforms.py` for examples.
- Data stored in MongoDB often has timestamps serialized to ISO strings before insert; endpoints convert back to datetime when reading.
- Pydantic models in backend sometimes set `model_config = ConfigDict(extra="ignore")` to ignore MongoDB `_id` fields. Respect these configs when adding new models.
- The frontend uses `craco` instead of raw react-scripts; modify `craco.config.js` when changing webpack/postcss/tailwind behavior.

Tests, linters and formatting
- Backend dev tools listed in `requirements.txt`: `pytest`, `black`, `isort`, `flake8`, `mypy` — run tests with `pytest` from `app/backend` and formatting via `black .`.
- Frontend tests use CRA tooling (`yarn test`). ESLint config is present via devDependencies.

PR/branch and commit conventions (keep these):
- Small, focused PRs
- Branch naming: `feat/<short>`, `fix/<short>`, `docs/<short>`
- Commit message format: `<type>(<scope>): <short summary>` e.g. `feat(api): add health endpoint`

When you add CI
- Add a minimal workflow under `.github/workflows/` that runs backend tests (`pip install -r backend/requirements.txt && pytest`) and frontend (`yarn install && yarn test --ci`).

Key places to inspect when working in this repo:
- `app/backend/` — API, routes, requirements
- `app/frontend/` — React app, `craco` config, `package.json`
- `.env` files (local only) and `README.md`

If anything is unclear (intended deployment target, DB connection details, or CI requirements), stop and ask the human maintainer rather than guessing. Provide detection results (which manifests you found) and a short plan of the next change you propose.

-- End of file --
````
