# SentinelIQ (local MVP)

AI-powered competitive intelligence platform. Seeded records are fictional demo data (`is_demo=true`).

## Backend setup (Windows PowerShell)

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
alembic upgrade head
python -m scripts.seed
python -m app.ml.train
python -m pytest -q
ruff check .
uvicorn app.main:app --reload
```

The API is available at `http://127.0.0.1:8000/docs` with the `/api/v1` prefix.

## Current MVP workflow

Collect a source with `POST /api/v1/sources/{source_id}/collect`. New observations are normalized,
deduplicated, linked to candidate events, evidence-checked, classified when a trained model is available,
and given one explainable heuristic risk assessment. Missing model artifacts are reported in the collection
response and do not block evidence or risk persistence.

Reports are generated from persisted company data:

```powershell
curl.exe -X POST http://127.0.0.1:8000/api/v1/reports `
  -H "Content-Type: application/json" `
  -d '{"company_id":1}'
curl.exe "http://127.0.0.1:8000/api/v1/reports/1/export?format=markdown" -o report.md
curl.exe "http://127.0.0.1:8000/api/v1/reports/1/export?format=json" -o report.json
```

## ML

```powershell
python -m app.ml.train
python -m app.ml.evaluate
```

The bundled dataset is synthetic and template-generated. Held-out metrics are demonstration metrics only
and do not establish real-world accuracy. Evidence verification means that a cited excerpt exists in stored
data; it does not establish that the source claim is true.

## Frontend

```powershell
cd frontend
npm install
npm run typecheck
npm run lint
npm run build
npm run dev
```

The frontend includes Overview, Companies, company profiles, Feed, Event detail, Risk, Reports, Settings,
Watchlists, Events & Evidence, Analytics, ML Lab, and Sources. The primary workspace uses localStorage-backed
prototype records for UI exploration; the ML Lab calls the real backend ML endpoints and does not fake training
results.
The mock provider records simulated deliveries only; it never sends real email or WhatsApp messages.

To train with a supplied CSV, use the required `text,label` columns:

```powershell
python -m app.ml.train --data C:\path\your_dataset.csv --model app\ml\artifacts\model.joblib --metrics app\ml\artifacts\metrics.json
```

See `docs/ROADMAP.md` and `docs/CODEX_HANDOFF.md` for verified scope and remaining work.
