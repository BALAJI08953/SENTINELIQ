# API Surface

The FastAPI application uses `/api/v1`.

Core groups:

- `/companies`, `/companies/{id}/sources`, `/sources/{id}/collect`
- `/observations`, `/events`, `/events/{id}/process`, `/events/{id}/risk`
- `/events/{id}/insights`, `/events/{id}/decision-support`
- `/risk-assessments`, `/analytics/*`, `/settings`
- `/reports`, `/reports/{id}/export`
- `/workflows`, `/workflows/{id}/schedules`, `/schedules/{id}/recipients`
- `/workflows/{id}/execute`, `/delivery-logs`, `/notification-providers`

FastAPI OpenAPI docs are available at `/docs` when the backend is running.
