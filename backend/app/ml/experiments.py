import json
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import joblib
import pandas as pd

from app.ml.paths import ARTIFACTS, DATA_PATH
from app.ml.predict import predict
from app.ml.train import dataset_fingerprint, train
from app.models.entities import EVENT_CATEGORIES

PROJECT_ROOT = Path(__file__).resolve().parents[3]
EXPERIMENTS_PATH = ARTIFACTS / "experiments.json"


def resolve_dataset(path: str | None) -> Path:
    raw = Path(path) if path else DATA_PATH
    resolved = raw if raw.is_absolute() else PROJECT_ROOT / raw
    resolved = resolved.resolve()
    allowed_roots = [PROJECT_ROOT.resolve()]
    if not any(resolved == root or root in resolved.parents for root in allowed_roots):
        raise ValueError("Dataset path must stay inside the SentinelIQ project directory")
    if resolved.suffix.lower() != ".csv":
        raise ValueError("Only CSV datasets are supported")
    if not resolved.exists():
        raise ValueError(f"Dataset not found: {resolved}")
    return resolved


def validate_dataset(path: str | None = None, text_column: str = "text", target_column: str = "label") -> dict:
    dataset = resolve_dataset(path)
    df = pd.read_csv(dataset)
    missing = [c for c in [text_column, target_column] if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required column(s): {', '.join(missing)}")
    total_rows = len(df)
    duplicate_rows = int(df.duplicated(subset=[text_column, target_column]).sum())
    invalid_mask = df[text_column].isna() | df[target_column].isna()
    normalized = df[[text_column, target_column]].copy()
    normalized[text_column] = normalized[text_column].fillna("").astype(str).str.strip()
    normalized[target_column] = normalized[target_column].fillna("").astype(str).str.strip()
    invalid_mask |= normalized[text_column].eq("") | normalized[target_column].eq("")
    valid_df = normalized.loc[~invalid_mask]
    labels = sorted(set(valid_df[target_column]))
    unknown = sorted(set(labels) - set(EVENT_CATEGORIES))
    counts = valid_df[target_column].value_counts().to_dict()
    valid = not unknown and not missing and len(valid_df) > 0 and all(v >= 2 for v in counts.values())
    return {
        "path": str(dataset.relative_to(PROJECT_ROOT)),
        "fingerprint_sha256": dataset_fingerprint(dataset),
        "columns": list(df.columns),
        "row_count": total_rows,
        "valid_row_count": int((~invalid_mask).sum()),
        "invalid_row_count": int(invalid_mask.sum()),
        "duplicate_row_count": duplicate_rows,
        "labels": labels,
        "label_counts": counts,
        "unknown_labels": unknown,
        "supported_labels": EVENT_CATEGORIES,
        "is_valid": valid,
        "validation_errors": _validation_errors(missing, unknown, counts, int((~invalid_mask).sum())),
    }


def train_experiment(
    path: str | None = None,
    task: str = "competitive_event_classification",
    text_column: str = "text",
    target_column: str = "label",
) -> dict:
    if task != "competitive_event_classification":
        raise ValueError("Only competitive_event_classification is implemented for real training")
    if text_column != "text" or target_column != "label":
        raise ValueError("Current trainer expects text_column='text' and target_column='label'")
    validation = validate_dataset(path, text_column, target_column)
    if not validation["is_valid"]:
        raise ValueError("; ".join(validation["validation_errors"]))
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    exp_id = f"exp_{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}"
    model_path = ARTIFACTS / f"{exp_id}.joblib"
    metrics_path = ARTIFACTS / f"{exp_id}.metrics.json"
    metrics = train(resolve_dataset(path), model_path=model_path, metrics_path=metrics_path)
    record = {
        "id": exp_id,
        "task": task,
        "status": "completed",
        "dataset": validation,
        "artifact_path": str(model_path.relative_to(PROJECT_ROOT)),
        "metrics_path": str(metrics_path.relative_to(PROJECT_ROOT)),
        "metrics": metrics,
        "created_at": datetime.now(UTC).isoformat(),
    }
    records = list_experiments()
    records.insert(0, record)
    EXPERIMENTS_PATH.write_text(json.dumps(records, indent=2), encoding="utf-8")
    return record


def list_experiments() -> list[dict[str, Any]]:
    if not EXPERIMENTS_PATH.exists():
        return []
    return json.loads(EXPERIMENTS_PATH.read_text(encoding="utf-8"))


def get_experiment(exp_id: str) -> dict:
    for exp in list_experiments():
        if exp["id"] == exp_id:
            return exp
    raise ValueError(f"Experiment not found: {exp_id}")


def predict_with_experiment(exp_id: str, text: str) -> dict:
    exp = get_experiment(exp_id)
    model_path = PROJECT_ROOT / exp["artifact_path"]
    loaded = joblib.load(model_path)
    pred = predict(text, model_path)
    return {
        "experiment_id": exp_id,
        "model_version": loaded["version"],
        "label": pred.label,
        "confidence": pred.confidence,
        "input_text": text,
    }


def _validation_errors(missing: list[str], unknown: list[str], counts: dict, valid_rows: int) -> list[str]:
    errors = []
    if missing:
        errors.append(f"missing columns: {', '.join(missing)}")
    if unknown:
        errors.append(f"unknown labels: {', '.join(unknown)}")
    if valid_rows == 0:
        errors.append("dataset has no valid non-empty rows")
    low = [label for label, count in counts.items() if count < 2]
    if low:
        errors.append(f"labels need at least two examples: {', '.join(low)}")
    return errors
