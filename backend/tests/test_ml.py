import pytest

from app.ml import predict as predict_mod
from app.ml.evaluate import compute_metrics
from app.ml.preprocessing import preprocess
from app.ml.train import load_dataset, split_data, train
from app.models import Company, Event
from app.models.entities import EVENT_CATEGORIES


@pytest.fixture(scope="module")
def trained(tmp_path_factory):
    d = tmp_path_factory.mktemp("ml")
    m = train(model_path=d / "m.joblib", metrics_path=d / "metrics.json")
    return d / "m.joblib", m


def test_preprocess():
    assert preprocess("<b>Acme</b>  RAISES $5M!!") == "acme  raises $5m".replace("  ", " ")


def test_dataset_is_labeled_synthetic_and_covers_classes():
    import pandas as pd

    from app.ml.paths import DATA_PATH
    df = pd.read_csv(DATA_PATH)
    assert set(df["synthetic"]) == {True}
    assert set(df["label"]) == set(EVENT_CATEGORIES)


def test_metrics_structure_and_consistency(trained):
    _, m = trained
    n = len(m["labels"])
    assert len(m["confusion_matrix"]) == n and all(len(r) == n for r in m["confusion_matrix"])
    assert sum(map(sum, m["confusion_matrix"])) == m["n_test"]
    assert 0 <= m["accuracy"] <= 1 and 0 <= m["macro_f1"] <= 1
    assert "SYNTHETIC" in m["disclaimer"]


def test_compute_metrics_matches_manual_accuracy(trained):
    import joblib
    path, _ = trained
    pipe = joblib.load(path)["pipeline"]
    X, y = load_dataset()
    _, X_te, _, y_te = split_data(X, y)
    manual = sum(p == t for p, t in zip(pipe.predict(X_te), y_te, strict=True)) / len(y_te)
    assert compute_metrics(pipe, X_te, y_te)["accuracy"] == pytest.approx(manual)


def test_predict_returns_valid_label_and_confidence(trained):
    path, _ = trained
    p = predict_mod.predict("Acme raises $20 million in a Series B round", path)
    assert p.label in EVENT_CATEGORIES and 0 <= p.confidence <= 1


def test_missing_model_raises_not_fake_success(tmp_path):
    with pytest.raises(predict_mod.ModelNotAvailableError):
        predict_mod.predict("anything", tmp_path / "nope.joblib")


def test_classify_event_persists_prediction(db, trained):
    path, _ = trained
    c = Company(name="A")
    db.add(c)
    db.flush()
    e = Event(company_id=c.id, title="A appoints a new chief executive officer")
    db.add(e)
    db.commit()
    row = predict_mod.classify_event(db, e, path)
    assert row.id and row.model_version.startswith("tfidf-lr-")
    assert e.category == row.label or row.confidence < predict_mod.MIN_CONFIDENCE_TO_RELABEL
