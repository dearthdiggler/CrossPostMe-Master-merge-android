
# CrossPostMe AI Agent Instructions

Authoritative, actionable guidance for AI agents working in this repo.

## Repository Layout

- `app/backend/` — FastAPI backend (entry: `server.py`, routes: `routes/`, models: `models.py`).
- `app/frontend/` — React frontend (CRA + CRACO, Tailwind, shadcn/ui).
- Android/iOS folders: starter templates reference backend models/services for mobile clients.

## Architecture & Data Flow

- Backend migrated from MongoDB to Supabase (see README.md for migration notes). Ignore legacy Motor/MongoDB code unless maintaining old endpoints.
- Backend entry: `app/backend/server.py` mounts routers from `routes/` and manages DB client lifecycle. Environment variables loaded via `.env` (see `.env.example`).
- API routes: Each file in `app/backend/routes/` exports `router = APIRouter(...)` and is included in `server.py`.
- Data models: Pydantic models in `models.py` use `model_config = ConfigDict(extra="ignore")` to ignore DB-specific fields.
- Datetime fields are always serialized as ISO strings before DB insert; deserialize on read.
- Query pattern: Use `.to_list(1000)` for list endpoints, then map results to Pydantic models.

## Developer Workflows

### Backend
- Create venv, install, run dev server:
	```powershell
	python -m venv .venv; .\.venv\Scripts\Activate.ps1
	pip install -r .\app\backend\requirements.txt
	uvicorn server:app --reload --host 0.0.0.0 --port 8000 --app-dir .\app\backend
	```
- Tests: `pytest` (see `app/backend/tests/README.md` for markers and structure)
- Formatting: `black .`, lint: `flake8`, type-check: `mypy`

### Frontend
- Dev server:
	```powershell
	cd .\app\frontend
	yarn install
	yarn start
	```
- API calls: Use `api.js` helper (cookie-based auth, auto-refresh on 401, see `src/lib/api.js`).
- UI: Compose from `src/components/` and `src/components/ui/` (shadcn/ui pattern).
- Tests: `yarn test` (CRA runner), E2E: `yarn test:e2e` (Playwright)

### Security & Environment
- Copy `.env.example` to `.env` and generate encryption keys as described in `app/README.md`.
- Never commit secrets. Use secrets managers for production (see README).

### Deployment
- Use provided Dockerfiles and `docker-compose.yml` for containerized runs.
- Backend loads `.env` via `dotenv` in `server.py`.

## Project-Specific Patterns
- Backend: Always reuse shared DB client from `server.py` or dependency-injected `get_db()`.
- Frontend: Use `api.js` for all API calls; do not manually set auth headers.
- Mobile: Reference backend models/services for API logic; port business logic as needed.

## Key Example Files
- `app/backend/routes/ads.py`, `platforms.py`, `ai.py` — router + DB usage
- `app/backend/server.py` — app entry, CORS, DB client
- `app/frontend/package.json`, `craco.config.js`, `src/components/` — frontend structure

## CI/CD
- If adding CI, create `.github/workflows/` to run:
	- `pip install -r app/backend/requirements.txt && pytest`
	- `cd app/frontend && yarn install && yarn test --ci`

## If Unclear
- If deployment target, DB credentials, or CI expectations are unclear, stop and ask a maintainer. List which manifests you inspected and your plan for the change.
