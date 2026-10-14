import json

import pytest

from app.ml.experiments import (
    get_experiment,
    predict_with_experiment,
    train_experiment,
    validate_dataset,
)


def write_csv(path, rows):
    path.write_text("text,label\n" + "\n".join(rows), encoding="utf-8")


def configure_tmp_project(monkeypatch, tmp_path):
    from app.ml import experiments as exp_mod

    artifacts = tmp_path / "backend" / "app" / "ml" / "artifacts"
    monkeypatch.setattr(exp_mod, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(exp_mod, "ARTIFACTS", artifacts)
    monkeypatch.setattr(exp_mod, "EXPERIMENTS_PATH", artifacts / "experiments.json")
    return exp_mod


def test_validate_dataset_reports_schema_and_labels(tmp_path, monkeypatch):
    configure_tmp_project(monkeypatch, tmp_path)
    data = tmp_path / "bad.csv"
    write_csv(data, ["hello,unknown_label", ",pricing_change", "valid,pricing_change"])
    result = validate_dataset(str(data))
    assert result["is_valid"] is False
    assert "unknown_label" in result["unknown_labels"]
    assert result["invalid_row_count"] == 1
    assert result["duplicate_row_count"] == 0


def test_train_experiment_persists_metadata_and_predicts(tmp_path, monkeypatch):
    configure_tmp_project(monkeypatch, tmp_path)
    rows = [
        "A launches a product,product_launch",
        "B launches a product,product_launch",
        "C launches a product,product_launch",
        "D launches a product,product_launch",
        "A signs partner,partnership",
        "B signs partner,partnership",
        "C signs partner,partnership",
        "D signs partner,partnership",
        "A expands to Europe,expansion",
        "B expands to Asia,expansion",
        "C expands to Africa,expansion",
        "D expands to America,expansion",
    ]
    data = tmp_path / "events.csv"
    write_csv(data, rows)
    artifacts = tmp_path / "backend" / "app" / "ml" / "artifacts"

    result = train_experiment(str(data))

    assert result["status"] == "completed"
    assert result["metrics"]["baseline"]["model_type"] == "most_frequent_dummy"
    assert result["metrics"]["dataset"]["rows"] == 12
    assert get_experiment(result["id"])["id"] == result["id"]
    pred = predict_with_experiment(result["id"], "Company launches a new product suite")
    assert pred["label"] in {"product_launch", "partnership", "expansion"}
    assert 0 <= pred["confidence"] <= 1
    assert json.loads((artifacts / "experiments.json").read_text(encoding="utf-8"))[0]["id"] == result["id"]


def test_train_rejects_non_event_task(tmp_path, monkeypatch):
    configure_tmp_project(monkeypatch, tmp_path)
    data = tmp_path / "events.csv"
    write_csv(data, ["A launches,product_launch", "B launches,product_launch"])
    with pytest.raises(ValueError, match="Only competitive_event_classification"):
        train_experiment(str(data), task="financial_movement_classification")
