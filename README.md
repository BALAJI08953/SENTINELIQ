# SentinelIQ (base project, in progress)

AI-powered competitive intelligence platform. **Status: Stages 1-2 of 7 complete** (models, migration, seed, risk scoring, company/source services, ingestion, dedup, event extraction).
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
ML classifier, API routes, frontend, scheduler, notifications, reports, full docs. See `docs/ROADMAP.md` once created.
