# SentinelIQ Roadmap

## Verified

- Company, source, observation, event, evidence, prediction, risk, relationship, report, and workflow models.
- RSS/HTML/demo source collection with normalization, content-hash deduplication, source status/error tracking,
  and robots.txt handling.
- Candidate event extraction with unique event/observation evidence links.
- TF-IDF plus Logistic Regression training, held-out metrics, saved model artifact, and explicit missing-model errors.
- Explainable heuristic risk scoring with bounded factors and evidence-quality derivation.
- FastAPI CRUD, analytics, settings, event processing, report generation, and Markdown/JSON report exports.
- Deterministic local insights, hypothetical decision-support options, workflow configuration, opt-in APScheduler
  singleton, and simulated email/WhatsApp delivery logs.
- React overview, companies, company profile, feed, event detail, risk, reports, and settings pages use API data.

## Next

1. Add scheduler job registration and per-source retry with bounded concurrency.
2. Apply `show_demo_data` consistently to analytics, feed, reports, and profile queries.
3. Add browser-level frontend tests for collection, report generation, and workflow execution.
4. Replace the synthetic classifier dataset with reviewed, versioned labels before using metrics for decisions.
5. Add an external dataset import adapter with provenance and license metadata.

## Out of scope for this MVP slice

Real email/WhatsApp delivery, enterprise identity and permissions, broad crawling, foundation-model training,
Kubernetes, billing, and production deployment automation.
