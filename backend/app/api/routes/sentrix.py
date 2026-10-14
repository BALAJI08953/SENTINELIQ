from datetime import datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.services.sentrix import answer

router = APIRouter(prefix="/sentrix", tags=["sentrix"])


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=10000)
    company_id: int | None = None
    event_id: int | None = None
    experiment_id: str | None = None
    start: datetime | None = None
    end: datetime | None = None


@router.post("/chat")
def chat(body: ChatRequest, db: Session = Depends(get_db)):
    result = answer(db, body.message, company_id=body.company_id, event_id=body.event_id,
                    experiment_id=body.experiment_id, start=body.start, end=body.end)
    return {"assistant": "SENTRIX", "answer": result.answer, "provider": result.provider,
            "citations": result.citations, "records": result.records}


@router.get("/status")
def status():
    return {
        "assistant": "SENTRIX",
        "provider": "deterministic_grounded" if settings.llm_provider.lower() in {"", "deterministic", "none"} else settings.llm_provider,
        "llm_configured": bool(settings.llm_base_url and settings.llm_api_key and settings.llm_model),
    }
