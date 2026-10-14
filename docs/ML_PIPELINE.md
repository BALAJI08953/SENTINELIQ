# ML Pipeline

The local classifier uses TF-IDF features and Logistic Regression over event text. The supported labels are
`pricing_change`, `product_launch`, `partnership`, `funding`, `leadership_change`, `regulatory_change`,
`acquisition`, `expansion`, and `other`.

The bundled CSV is synthetic and template-generated. It is suitable for testing the pipeline only and must not
be presented as real-world model performance. The implemented real training task is
`competitive_event_classification`; it is separate from financial stock-movement classification, sentiment
classification, anomaly detection, and business-risk assessment.

Metrics are calculated from a held-out stratified split and include accuracy, macro-F1, per-class precision/
recall/F1, support, a confusion matrix, and a most-frequent baseline. The model artifact and experiment metadata
are written under `backend/app/ml/artifacts/`, which is excluded from Git.

Train with the default sample:

```powershell
python -m app.ml.train
```

Train with a supplied dataset:

```powershell
python -m app.ml.train --data C:\path\events.csv --model app\ml\artifacts\event_classifier.joblib --metrics app\ml\artifacts\metrics.json
```

The supplied CSV must contain non-empty `text` and `label` columns. Each label needs at least two rows for the
stratified split. Dataset provenance and license information should be recorded before using external data.

## API workflow

With the backend running:

```powershell
curl.exe -X POST http://127.0.0.1:8000/api/v1/ml/datasets/validate `
  -H "Content-Type: application/json" `
  -d '{"path":"sample_data/training_examples.csv"}'

curl.exe -X POST http://127.0.0.1:8000/api/v1/ml/experiments/train `
  -H "Content-Type: application/json" `
  -d '{"path":"sample_data/training_examples.csv","task":"competitive_event_classification"}'

curl.exe http://127.0.0.1:8000/api/v1/ml/experiments
```

The ML Lab page calls these backend operations directly. It does not fabricate metrics when the backend is
unavailable. Inference requires a completed experiment id and a non-empty text input.

## Dataset status

The Two Sigma competition and the stock-news dataset were not downloaded or processed automatically. Their
current availability, schema, and licensing could not be verified from this environment. Place a permitted local
CSV inside the project directory, validate it first, and keep the target definition separate from sentiment and
business-risk tasks.
