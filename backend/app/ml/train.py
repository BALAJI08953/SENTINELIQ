"""Train TF-IDF + Logistic Regression. CLI: python -m app.ml.train"""
import json
from datetime import UTC, datetime

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

from app.ml.paths import ARTIFACTS, DATA_PATH, METRICS_PATH, MODEL_PATH
from app.ml.preprocessing import preprocess
from app.models.entities import EVENT_CATEGORIES

SEED = 42


def load_dataset(path=DATA_PATH):
    df = pd.read_csv(path).dropna(subset=["text", "label"])
    bad = set(df["label"]) - set(EVENT_CATEGORIES)
    if bad:
        raise ValueError(f"Unknown labels in dataset: {sorted(bad)}")
    return df["text"].tolist(), df["label"].tolist()


def split_data(X, y):
    return train_test_split(X, y, test_size=0.25, stratify=y, random_state=SEED)


def build_pipeline() -> Pipeline:
    return Pipeline([
        ("tfidf", TfidfVectorizer(preprocessor=preprocess, ngram_range=(1, 2), min_df=1, sublinear_tf=True)),
        ("clf", LogisticRegression(max_iter=1000, C=5.0, random_state=SEED)),
    ])


def train(path=DATA_PATH, model_path=MODEL_PATH, metrics_path=METRICS_PATH) -> dict:
    from app.ml.evaluate import compute_metrics

    X, y = load_dataset(path)
    X_tr, X_te, y_tr, y_te = split_data(X, y)
    pipe = build_pipeline().fit(X_tr, y_tr)
    metrics = compute_metrics(pipe, X_te, y_te)
    version = datetime.now(UTC).strftime("tfidf-lr-%Y%m%d%H%M%S")
    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({"pipeline": pipe, "version": version, "n_train": len(X_tr)}, model_path)
    metrics_path.write_text(json.dumps({"version": version, **metrics}, indent=2))
    return {"version": version, **metrics}


if __name__ == "__main__":
    m = train()
    print(f"trained {m['version']}: accuracy={m['accuracy']:.3f} macro_f1={m['macro_f1']:.3f} (n_test={m['n_test']})")
    print(m["disclaimer"])
    ARTIFACTS.mkdir(exist_ok=True)
