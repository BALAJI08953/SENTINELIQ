from datetime import datetime
from typing import Generic, Literal, TypeVar

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

T = TypeVar("T")
Category = Literal["pricing_change", "product_launch", "partnership", "funding", "leadership_change",
                   "regulatory_change", "acquisition", "expansion", "other"]
RelType = Literal["competitor", "customer", "supplier", "partner", "stakeholder", "other"]


class ORM(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class Page(BaseModel, Generic[T]):
    items: list[T]
    total: int
    offset: int
    limit: int


class CompanyIn(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    website: HttpUrl | None = None
    industry: str | None = Field(default=None, max_length=120)
    description: str | None = None


class CompanyUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    website: HttpUrl | None = None
    industry: str | None = Field(default=None, max_length=120)
    description: str | None = None


class CompanyOut(ORM):
    id: int
    name: str
    website: str | None
    industry: str | None
    description: str | None
    is_demo: bool


class SourceIn(BaseModel):
    kind: Literal["rss", "html", "demo"]
    url: str = Field(min_length=1, max_length=1000)
    label: str | None = None


class SourceOut(ORM):
    id: int
    company_id: int
    kind: str
    url: str
    label: str | None
    is_demo: bool
    enabled: bool
    last_status: str | None
    last_error: str | None
    last_collected_at: datetime | None


class ObservationOut(ORM):
    id: int
    source_id: int
    company_id: int
    title: str
    body: str
    url: str | None
    published_at: datetime | None
    collected_at: datetime
    is_demo: bool


class EvidenceOut(ORM):
    id: int
    observation_id: int
    excerpt: str | None
    verification_status: str


class PredictionOut(ORM):
    id: int
    label: str
    confidence: float
    model_version: str


class RiskIn(BaseModel):
    impact: float = Field(ge=0, le=10)
    urgency: float = Field(ge=0, le=10)
    strategic_relevance: float = Field(ge=0, le=10)
    evidence_quality: float | None = Field(default=None, ge=0, le=10)


class RiskOut(ORM):
    id: int
    event_id: int
    impact: float
    urgency: float
    strategic_relevance: float
    evidence_quality: float
    overall_score: float
    priority: str
    explanation: str
    created_at: datetime


class EventOut(ORM):
    id: int
    company_id: int
    title: str
    category: str
    status: str
    occurred_at: datetime
    is_demo: bool


class EventDetail(EventOut):
    evidence: list[EvidenceOut]
    predictions: list[PredictionOut]
    risk_assessments: list[RiskOut]


class EventUpdate(BaseModel):
    status: Literal["new", "reviewed", "dismissed"] | None = None
    category: Category | None = None


class FeedbackIn(BaseModel):
    correct_category: Category | None = None
    useful: bool | None = None
    comment: str | None = Field(default=None, max_length=2000)


class FeedbackOut(ORM, FeedbackIn):
    id: int
    event_id: int


class RelationshipIn(BaseModel):
    related_company_id: int
    relationship_type: RelType
    verification_status: Literal["unverified", "verified"] = "unverified"
    evidence_observation_id: int | None = None


class RelationshipOut(ORM):
    id: int
    company_id: int
    related_company_id: int
    relationship_type: str
    verification_status: str
    evidence_observation_id: int | None


class SettingsIO(BaseModel):
    timezone: str = Field(default="UTC", max_length=64)
    display_name: str | None = Field(default=None, max_length=120)
    show_demo_data: bool = True


class ReportCreate(BaseModel):
    company_id: int
    start: datetime | None = None
    end: datetime | None = None


class ReportOut(ORM):
    id: int
    report_type: str
    title: str
    company_id: int | None
    content_json: dict
    content_markdown: str
    is_demo: bool
    created_at: datetime


class WorkflowIn(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    enabled: bool = True
    company_ids: list[int] = Field(default_factory=list)
    categories: list[Category] = Field(default_factory=list)
    min_priority: Literal["low", "medium", "high", "critical"] = "low"
    report_type: Literal["daily", "weekly", "company", "high_priority"] = "daily"


class WorkflowPatch(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    enabled: bool | None = None
    company_ids: list[int] | None = None
    categories: list[Category] | None = None
    min_priority: Literal["low", "medium", "high", "critical"] | None = None
    report_type: Literal["daily", "weekly", "company", "high_priority"] | None = None


class WorkflowOut(ORM):
    id: int
    name: str
    enabled: bool
    company_ids: list[int]
    categories: list[str]
    min_priority: str
    report_type: str


class ScheduleIn(BaseModel):
    mode: Literal["daily", "interval"]
    time_of_day: str | None = Field(default=None, pattern=r"^\d{2}:\d{2}$")
    interval_minutes: int | None = Field(default=None, ge=1)
    timezone: str = Field(default="UTC", max_length=64)


class ScheduleOut(ORM):
    id: int
    workflow_id: int
    mode: str
    time_of_day: str | None
    interval_minutes: int | None
    timezone: str


class RecipientIn(BaseModel):
    channel: Literal["email", "whatsapp"]
    address: str = Field(min_length=1, max_length=300)
    authorized: bool = False


class RecipientOut(ORM):
    id: int
    schedule_id: int
    channel: str
    address: str
    authorized: bool


class DeliveryLogOut(ORM):
    id: int
    schedule_id: int | None
    report_id: int | None
    channel: str
    recipient: str
    provider: str
    status: str
    detail: str | None
    created_at: datetime
