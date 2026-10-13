"""Metrics computed from real held-out predictions. CLI: python -m app.ml.evaluate"""
import json

import joblib
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_recall_fscore_support,
)

from app.ml.paths import MODEL_PATH
from app.ml.train import load_dataset, split_data

DISCLAIMER = ("Computed on a held-out split of SYNTHETIC template data when the default dataset is used; "
              "this does not establish real-world reliability.")


def compute_metrics(model, X_test, y_test) -> dict:
    labels = sorted(set(y_test) | set(model.classes_))
    pred = model.predict(X_test)
    p, r, f, s = precision_recall_fscore_support(y_test, pred, labels=labels, zero_division=0)
    return {
        "n_test": len(y_test),
        "accuracy": float(accuracy_score(y_test, pred)),
        "macro_f1": float(f1_score(y_test, pred, labels=labels, average="macro", zero_division=0)),
        "per_class": {lab: {"precision": float(p[i]), "recall": float(r[i]), "f1": float(f[i]), "support": int(s[i])}
                      for i, lab in enumerate(labels)},
        "labels": labels,
        "confusion_matrix": confusion_matrix(y_test, pred, labels=labels).tolist(),
        "disclaimer": DISCLAIMER,
    }


def main() -> None:
    if not MODEL_PATH.exists():
        raise SystemExit("No trained model found. Run: python -m app.ml.train")
    model = joblib.load(MODEL_PATH)["pipeline"]
    X, y = load_dataset()
    _, X_test, _, y_test = split_data(X, y)
    print(json.dumps(compute_metrics(model, X_test, y_test), indent=2))


if __name__ == "__main__":
    main()
