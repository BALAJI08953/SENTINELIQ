from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.ml.experiments import (
    get_experiment,
    list_experiments,
    predict_with_experiment,
    train_experiment,
    validate_dataset,
)

router = APIRouter(prefix="/ml", tags=["ml"])


class DatasetRequest(BaseModel):
    path: str | None = Field(default=None, description="CSV path inside the project directory")
    text_column: str = "text"
    target_column: str = "label"


class TrainRequest(DatasetRequest):
    task: str = "competitive_event_classification"


class InferenceRequest(BaseModel):
    text: str = Field(min_length=1, max_length=5000)


@router.post("/datasets/validate")
def validate(body: DatasetRequest):
    return validate_dataset(body.path, body.text_column, body.target_column)


@router.post("/experiments/train")
def train(body: TrainRequest):
    return train_experiment(body.path, body.task, body.text_column, body.target_column)


@router.get("/experiments")
def experiments():
    return {"items": list_experiments()}


@router.get("/experiments/{experiment_id}")
def experiment(experiment_id: str):
    return get_experiment(experiment_id)


@router.post("/experiments/{experiment_id}/predict")
def inference(experiment_id: str, body: InferenceRequest):
    return predict_with_experiment(experiment_id, body.text)
