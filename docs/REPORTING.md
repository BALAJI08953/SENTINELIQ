# Reporting

`POST /api/v1/reports` generates a company report from persisted observations, events, evidence, predictions,
and risk assessments. Reports are stored in the `reports` table and can be listed or retrieved.

Exports:

- `GET /api/v1/reports/{id}/export?format=markdown`
- `GET /api/v1/reports/{id}/export?format=json`

Reports label model output as a model signal and include limitations. Empty periods are valid and produce an
explicit empty section instead of invented content.
