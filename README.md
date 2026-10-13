# SentinelIQ (base project, in progress)

AI-powered competitive intelligence platform. **Status: Stages 1-5 of 7 complete** (models, migration, seed, risk scoring, company/source services, ingestion, dedup, event extraction, ML classifier, evidence checks, risk assessment service).
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
Scheduler, notifications, reports, full docs. See `docs/ROADMAP.md` once created.

## ML (stage 3)
```powershell
cd backend
python -m app.ml.train      # trains TF-IDF + Logistic Regression, writes app/ml/artifacts/
python -m app.ml.evaluate   # prints accuracy, macro-F1, per-class P/R, confusion matrix
```
**Caveat:** the bundled dataset is synthetic and template-generated; the same templates appear in the
train and test splits, so scores near 1.0 are inflated and prove nothing about real-world accuracy.
Evidence "verified" means the cited excerpt exists in a stored observation, not that the claim is true.

## API (stage 4)
```powershell
cd backend
uvicorn app.main:app --reload     # http://127.0.0.1:8000/docs (OpenAPI), prefix /api/v1
```
24 paths: health, companies (CRUD, events, timeline, sources, relationships), source collection, observations,
events (filters, detail, update, process, feedback), risk assessments, analytics (overview, timeline, categories,
priorities, companies), settings. **Not yet implemented:** reports, workflows, notifications, AI insights,
decision support. Errors use `{"error": {"code", "message"}}` (404 / 409 / 422 / 503 when no model is trained).

## Frontend (stage 5)
```powershell
cd frontend
npm install
npm run dev          # http://localhost:5173 (proxies /api to http://127.0.0.1:8000)
npm run typecheck; npm run lint; npm run build
```
Start the backend first (see API section). Pages: Overview (charts from live API data), Companies, Company profile
(sources, collect, events, observations, relationships), Intelligence feed, Event detail, Risk assessments, Settings.
**Reports and Workflows pages are honest placeholders**; their backends arrive in stage 6.
Decision support on the event page is also a labeled placeholder. Settings "show demo data" is stored but not yet applied.
