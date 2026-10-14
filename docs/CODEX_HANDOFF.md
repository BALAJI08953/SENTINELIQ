# Codex Handoff

## What changed

The persisted intelligence path now continues after source collection: new observations become events with
evidence, are classified when `app/ml/artifacts/model.joblib` exists, and receive one explainable risk assessment.
Rerunning collection or processing does not create duplicate observations, predictions for the same model version,
or risk assessments for the same event.

The report service builds company reports only from stored observations, events, evidence, predictions, and risk
assessments. `POST /api/v1/reports` persists rendered JSON and Markdown; `/export` supports `markdown` and `json`.
Model-generated predictions are labeled as model signals and limitations are included in every report.

Workflow endpoints now persist workflow configuration, daily/interval schedules, recipients, execution reports,
and mock delivery logs. The deterministic insights endpoints expose source facts, uncertainty, missing information,
and hypothetical decision options without requiring an external LLM API. The in-process APScheduler singleton is
available through `app.jobs.scheduler`; it is intentionally opt-in for local development.

The classifier CLI accepts `--data`, `--model`, and `--metrics`. A supplied dataset must contain non-empty
`text` and `label` columns using the supported event labels.

## Known limitations

The bundled training data is synthetic and template-generated; held-out metrics are demonstration metrics only.
Demo sources are seed-only and return no remote items. Workflows and delivery records are models/seed fixtures,
not a scheduler or real provider integration. The frontend stores the demo-data setting but does not yet apply it
to every query. No new database migration is required because the report table already exists in
`0001_initial_schema.py`.
