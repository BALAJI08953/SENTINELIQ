from dataclasses import dataclass

import joblib
from sqlalchemy.orm import Session

from app.ml.paths import MODEL_PATH
from app.models import Event, MLPrediction

MIN_CONFIDENCE_TO_RELABEL = 0.30


class ModelNotAvailableError(RuntimeError):
    """Raised instead of returning a fake prediction when no trained model exists."""


@dataclass
class Prediction:
    label: str
    confidence: float
    model_version: str


def load_model(path=MODEL_PATH) -> dict:
    if not path.exists():
        raise ModelNotAvailableError("No trained model. Run: python -m app.ml.train")
    return joblib.load(path)


def predict(text: str, path=MODEL_PATH) -> Prediction:
    bundle = load_model(path)
    probs = bundle["pipeline"].predict_proba([text])[0]
    i = int(probs.argmax())
    return Prediction(str(bundle["pipeline"].classes_[i]), float(probs[i]), bundle["version"])


def classify_event(db: Session, event: Event, path=MODEL_PATH) -> MLPrediction:
    """Store a prediction. The event category only changes when confidence is high enough."""
    pred = predict(event.title, path)
    row = MLPrediction(event_id=event.id, label=pred.label, confidence=pred.confidence,
                       model_version=pred.model_version)
    db.add(row)
    if pred.confidence >= MIN_CONFIDENCE_TO_RELABEL:
        event.category = pred.label
    db.commit()
    return row
