# AI Insights

`GET /api/v1/events/{event_id}/insights` returns a deterministic local interpretation built only from persisted
observations, evidence, predictions, and risk assessments. It includes source facts, possible implications,
uncertainties, missing information, suggested actions, and the provider name.

`GET /api/v1/events/{event_id}/decision-support` returns hypothetical response options. It does not select or
recommend a business action automatically. External LLM providers can be added behind the same service boundary
later, but must preserve evidence references and uncertainty labels.
