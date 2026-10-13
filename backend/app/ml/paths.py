from pathlib import Path

ARTIFACTS = Path(__file__).resolve().parent / "artifacts"
MODEL_PATH = ARTIFACTS / "event_classifier.joblib"
METRICS_PATH = ARTIFACTS / "metrics.json"
DATA_PATH = Path(__file__).resolve().parents[3] / "sample_data" / "training_examples.csv"
