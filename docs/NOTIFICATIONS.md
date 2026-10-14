# Notifications and Workflows

Workflows persist report type, company filters, category filters, minimum priority, and enabled state.
Schedules support daily time-of-day or interval modes with a stored timezone. Recipients support email and
WhatsApp channel labels.

`POST /api/v1/workflows/{id}/execute` generates persisted reports and records delivery attempts in
`delivery_logs`. The `mock` provider is development-only: authorized recipients receive `simulated` logs and
unauthorized recipients receive `failed` logs. No real message is sent.

The APScheduler singleton in `backend/app/jobs/scheduler.py` is opt-in. In-process scheduling is not durable
across restarts and should be replaced with a managed job runner for production.
