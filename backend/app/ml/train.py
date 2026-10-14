r"""Train TF-IDF + Logistic Regression.

Examples:
    python -m app.ml.train
    python -m app.ml.train --data ..\sample_data\training_examples.csv
"""
import argparse
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

import joblib
import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

from app.ml.paths import ARTIFACTS, DATA_PATH, METRICS_PATH, MODEL_PATH
from app.ml.preprocessing import preprocess
from app.models.entities import EVENT_CATEGORIES

SEED = 42


def dataset_fingerprint(path=DATA_PATH) -> str:
    p = Path(path)
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_dataset(path=DATA_PATH):
    df = pd.read_csv(path)
    required = {"text", "label"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Dataset must contain columns: text,label; missing {sorted(missing)}")
    df = df.dropna(subset=["text", "label"])
    df["text"] = df["text"].astype(str).str.strip()
    df["label"] = df["label"].astype(str).str.strip()
    df = df[df["text"].ne("") & df["label"].ne("")]
    if df.empty:
        raise ValueError("Dataset has no non-empty text/label rows")
    bad = set(df["label"]) - set(EVENT_CATEGORIES)
    if bad:
        raise ValueError(f"Unknown labels in dataset: {sorted(bad)}")
    return df["text"].tolist(), df["label"].tolist()


def split_data(X, y):
    counts = pd.Series(y).value_counts()
    if counts.min() < 2:
        raise ValueError("Every label needs at least two examples for a stratified train/test split")
    return train_test_split(X, y, test_size=0.25, stratify=y, random_state=SEED)


def build_pipeline() -> Pipeline:
    return Pipeline([
        ("tfidf", TfidfVectorizer(preprocessor=preprocess, ngram_range=(1, 2), min_df=1, sublinear_tf=True)),
        ("clf", LogisticRegression(max_iter=1000, C=5.0, random_state=SEED)),
    ])


def train(path=DATA_PATH, model_path=MODEL_PATH, metrics_path=METRICS_PATH) -> dict:
    from app.ml.evaluate import compute_metrics

    path = Path(path)
    model_path = Path(model_path)
    metrics_path = Path(metrics_path)
    X, y = load_dataset(path)
    X_tr, X_te, y_tr, y_te = split_data(X, y)
    pipe = build_pipeline().fit(X_tr, y_tr)
    metrics = compute_metrics(pipe, X_te, y_te)
    baseline = DummyClassifier(strategy="most_frequent").fit(X_tr, y_tr)
    baseline_metrics = compute_metrics(baseline, X_te, y_te)
    version = datetime.now(UTC).strftime("tfidf-lr-%Y%m%d%H%M%S")
    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({"pipeline": pipe, "version": version, "n_train": len(X_tr)}, model_path)
    out = {
        "version": version,
        "task": "competitive_event_classification",
        "dataset": {"path": str(path), "fingerprint_sha256": dataset_fingerprint(path), "rows": len(X)},
        "model_type": "tfidf_logistic_regression",
        "preprocessing": {"text": "html_strip_lowercase_punctuation_normalization", "vectorizer": "tfidf_1_2_grams"},
        "trained_at": datetime.now(UTC).isoformat(),
        "baseline": {
            "model_type": "most_frequent_dummy",
            "accuracy": baseline_metrics["accuracy"],
            "macro_f1": baseline_metrics["macro_f1"],
        },
        **metrics,
    }
    metrics_path.write_text(json.dumps(out, indent=2))
    return out


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train the SentinelIQ event classifier")
    parser.add_argument("--data", type=str, default=str(DATA_PATH), help="CSV with text,label columns")
    parser.add_argument("--model", type=str, default=str(MODEL_PATH), help="Output joblib path")
    parser.add_argument("--metrics", type=str, default=str(METRICS_PATH), help="Output metrics JSON path")
    args = parser.parse_args()
    m = train(path=args.data, model_path=args.model, metrics_path=args.metrics)
    print(f"trained {m['version']}: accuracy={m['accuracy']:.3f} macro_f1={m['macro_f1']:.3f} (n_test={m['n_test']})")
    print(m["disclaimer"])
    ARTIFACTS.mkdir(exist_ok=True)
