# SentinelIQ (base project, in progress)

AI-powered competitive intelligence platform. **Status: Stage 1 of 7 complete** (models, migration, seed, risk scoring).
All seeded data is FICTIONAL demo data (`is_demo=true`).

## Backend setup (Windows PowerShell)
```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
alembic upgrade head
python -m scripts.seed          # add --reset to reseed (drops all tables)
python -m pytest -q
ruff check .
```
Linux/macOS: replace the activate line with `source .venv/bin/activate`.

## Not yet built
Ingestion, ML classifier, API routes, frontend, scheduler, notifications, reports, full docs. See `docs/ROADMAP.md` once created.
