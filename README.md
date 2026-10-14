# SentinelIQ

SentinelIQ is a competitive-intelligence workspace for tracking companies, public source updates, evidence-backed events, risk signals, reports, workflows, and ML experiments. It includes a FastAPI backend, a React/Vite frontend, and SENTRIX, a grounded assistant that answers from persisted SentinelIQ records instead of inventing intelligence.

This repository is a local MVP/demo implementation. Seed data is fictional and marked with `is_demo=true`. Generated model metrics are demonstration metrics unless you train with your own documented dataset.

## What SentinelIQ Does

- Tracks company profiles, source configurations, observations, extracted events, evidence, and risk assessments.
- Collects permitted RSS/HTML sources, normalizes records, deduplicates observations, and stores provenance metadata.
- Separates source evidence from conclusions, model predictions, and rule-based risk scores.
- Generates reports from persisted intelligence records with export support.
- Provides workflow configuration, schedules, execution logs, and simulated delivery records.
- Runs an event-classification ML pipeline with dataset validation, experiment history, model artifacts, and held-out metrics.
- Provides SENTRIX as both a dedicated page and a floating assistant available across the app.

## Architecture

```text
backend/
  app/
    api/routes/        FastAPI route modules
    core/              configuration and database setup
    models/            SQLAlchemy models
    services/          business logic for ingestion, evidence, reports, workflows, SENTRIX
    ml/                training, prediction, experiments, metrics
    jobs/              scheduler wiring
  alembic/             database migrations
  tests/               backend test suite

frontend/
  src/
    pages/             application screens
    components/        layout, UI primitives, floating SENTRIX
    api/               API clients and prototype storage helpers
    types/             shared TypeScript interfaces

docs/                  feature notes, API notes, roadmap, security, ML pipeline
sample_data/           small documented sample training data
```

Backend data is stored in SQLite by default. Frontend API calls use `/api/v1` unless `VITE_API_BASE_URL` is set.

## SENTRIX Assistant

SENTRIX is the built-in intelligence assistant.

It supports:

- Floating chat on every application route.
- Dedicated `/sentrix` page.
- Route-aware context for selected company and event pages.
- Suggested questions, loading states, error handling, timestamps, answer copy, and citations.
- Grounded deterministic fallback when no LLM provider is configured.
- Optional OpenAI-compatible provider configuration through backend environment variables.

SENTRIX does not expose API keys in frontend code and does not fabricate citations. If there is no supporting record, it says so.

## Backend Setup

Windows PowerShell:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
alembic upgrade head
python -m scripts.seed
python -m app.ml.train
uvicorn app.main:app --reload
```

The API documentation is available at:

```text
http://127.0.0.1:8000/docs
```

The API prefix is:

```text
/api/v1
```

Useful backend checks:

```powershell
python -m pytest -q
ruff check .
python -c "from app.main import app; print(app.title)"
```

## Frontend Setup

Windows PowerShell:

```powershell
cd frontend
npm install
npm run dev
```

The Vite dev server will print the local browser URL. For production verification:

```powershell
npm run lint
npm run build
```

## Environment Variables

Create local environment files from `.env.example` when needed. Do not commit real `.env` files or credentials.

Common backend settings:

```text
SENTINELIQ_DATABASE_URL=sqlite:///./sentineliq.db
SENTINELIQ_CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
SENTINELIQ_LLM_PROVIDER=deterministic
SENTINELIQ_LLM_BASE_URL=
SENTINELIQ_LLM_API_KEY=
SENTINELIQ_LLM_MODEL=
```

Common frontend setting:

```text
VITE_API_BASE_URL=http://127.0.0.1:8000/api/v1
```

If the LLM settings are empty or `SENTINELIQ_LLM_PROVIDER=deterministic`, SENTRIX uses the local grounded fallback.

## Source Ingestion Workflow

1. Add a company.
2. Add a permitted RSS or HTML source for that company.
3. Collect the source:

```powershell
curl.exe -X POST "http://127.0.0.1:8000/api/v1/sources/1/collect"
```

Collection records source status, normalizes observations, deduplicates by content hash, extracts candidate events, verifies evidence traceability, and creates risk assessments. Network errors and inaccessible sources are stored as source status instead of being hidden.

## Reports

Reports are generated from persisted company intelligence records.

```powershell
curl.exe -X POST http://127.0.0.1:8000/api/v1/reports `
  -H "Content-Type: application/json" `
  -d '{"company_id":1}'

curl.exe "http://127.0.0.1:8000/api/v1/reports/1/export?format=markdown" -o report.md
curl.exe "http://127.0.0.1:8000/api/v1/reports/1/export?format=json" -o report.json
```

Reports include source references and timestamps where records exist.

## ML Pipeline

Train and evaluate the event classifier:

```powershell
cd backend
python -m app.ml.train
python -m app.ml.evaluate
```

Train with your own CSV:

```powershell
python -m app.ml.train --data C:\path\your_dataset.csv --model app\ml\artifacts\model.joblib --metrics app\ml\artifacts\metrics.json
```

Required CSV columns:

```text
text,label
```

The bundled dataset is synthetic/template-generated. Its metrics are useful for pipeline verification only and should not be presented as production accuracy.

## Real, Demo, and Simulated Boundaries

- Demo seed data is fictional and marked with `is_demo=true`.
- Evidence verification confirms traceability to stored text; it does not prove the external claim is true.
- Risk assessment is rule-based unless explicitly tied to a trained model output.
- Workflow delivery uses a mock/simulated provider unless real email or WhatsApp credentials are configured.
- SENTRIX fallback answers from stored records and clearly reports insufficient evidence.
- Generated model artifacts and local databases are ignored by Git.

## Verification Status

Latest verified local checks:

```text
Backend tests: 60 passed
Backend lint: ruff check backend passed
Frontend lint: npm run lint passed
Frontend build: npm run build passed
```

## Main Routes

Frontend pages:

- Overview
- Intelligence Feed
- Companies
- Company Profiles
- Watchlists
- Events & Evidence
- Event Detail
- Risk Assessments
- Analytics
- Reports
- Alerts & Workflows
- ML Lab
- Sources
- Settings
- SENTRIX Assistant

Backend route groups:

- `/api/v1/health`
- `/api/v1/companies`
- `/api/v1/sources`
- `/api/v1/observations`
- `/api/v1/events`
- `/api/v1/risk-assessments`
- `/api/v1/analytics/*`
- `/api/v1/reports`
- `/api/v1/workflows`
- `/api/v1/ml/*`
- `/api/v1/sentrix/*`

## Security Notes

- Do not commit `.env`, databases, generated model artifacts, large datasets, or credentials.
- Treat retrieved web content as untrusted input.
- Use only sources you are permitted to access.
- Keep external delivery providers disabled until credentials, recipient authorization, and provider status are verified.

## More Documentation

See:

- `docs/API.md`
- `docs/ML_PIPELINE.md`
- `docs/REPORTING.md`
- `docs/NOTIFICATIONS.md`
- `docs/AI_INSIGHTS.md`
- `docs/SECURITY.md`
- `docs/ROADMAP.md`
- `docs/CODEX_HANDOFF.md`
