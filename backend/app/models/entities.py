"""SQLAlchemy 2.x models for SentinelIQ.

Epistemic layers are kept in separate tables on purpose:
Observation/Evidence = source facts, MLPrediction = model output,
RiskAssessment = heuristic, Event.status/Feedback = human decisions.
"""
from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin, utcnow

EVENT_CATEGORIES = [
    "pricing_change", "product_launch", "partnership", "funding", "leadership_change",
    "regulatory_change", "acquisition", "expansion", "other",
]
RELATIONSHIP_TYPES = ["competitor", "customer", "supplier", "partner", "stakeholder", "other"]


class Company(Base, TimestampMixin):
    __tablename__ = "companies"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), unique=True, index=True)
    website: Mapped[str | None] = mapped_column(String(500))
    industry: Mapped[str | None] = mapped_column(String(120))
    description: Mapped[str | None] = mapped_column(Text)
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False)
    sources: Mapped[list["Source"]] = relationship(back_populates="company", cascade="all, delete-orphan")
    events: Mapped[list["Event"]] = relationship(back_populates="company", cascade="all, delete-orphan")


class Source(Base, TimestampMixin):
    __tablename__ = "sources"
    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), index=True)
    kind: Mapped[str] = mapped_column(String(20))  # rss | html | demo
    url: Mapped[str] = mapped_column(String(1000))
    label: Mapped[str | None] = mapped_column(String(200))
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    last_status: Mapped[str | None] = mapped_column(String(20))  # ok | error
    last_error: Mapped[str | None] = mapped_column(Text)
    last_collected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    company: Mapped[Company] = relationship(back_populates="sources")
    __table_args__ = (
        UniqueConstraint("company_id", "url", name="uq_source_company_url"),
        CheckConstraint("kind in ('rss','html','demo')", name="ck_source_kind"),
    )


class Observation(Base):
    __tablename__ = "observations"
    id: Mapped[int] = mapped_column(primary_key=True)
    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id", ondelete="CASCADE"), index=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(500))
    body: Mapped[str] = mapped_column(Text, default="")
    url: Mapped[str | None] = mapped_column(String(1000))
    content_hash: Mapped[str] = mapped_column(String(64))
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    collected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False)
    __table_args__ = (UniqueConstraint("company_id", "content_hash", name="uq_obs_company_hash"),)


class Event(Base, TimestampMixin):
    __tablename__ = "events"
    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(500))
    category: Mapped[str] = mapped_column(String(40), default="other", index=True)
    status: Mapped[str] = mapped_column(String(20), default="new")  # new|reviewed|dismissed
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False)
    company: Mapped[Company] = relationship(back_populates="events")
    evidence: Mapped[list["Evidence"]] = relationship(back_populates="event", cascade="all, delete-orphan")
    predictions: Mapped[list["MLPrediction"]] = relationship(back_populates="event", cascade="all, delete-orphan")
    risk_assessments: Mapped[list["RiskAssessment"]] = relationship(
        back_populates="event", cascade="all, delete-orphan"
    )


class Evidence(Base):
    __tablename__ = "evidence"
    id: Mapped[int] = mapped_column(primary_key=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id", ondelete="CASCADE"), index=True)
    observation_id: Mapped[int] = mapped_column(ForeignKey("observations.id", ondelete="CASCADE"), index=True)
    excerpt: Mapped[str | None] = mapped_column(Text)
    verification_status: Mapped[str] = mapped_column(String(20), default="unverified")
    event: Mapped[Event] = relationship(back_populates="evidence")
    __table_args__ = (UniqueConstraint("event_id", "observation_id", name="uq_evidence_pair"),)


class MLPrediction(Base):
    __tablename__ = "ml_predictions"
    id: Mapped[int] = mapped_column(primary_key=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id", ondelete="CASCADE"), index=True)
    label: Mapped[str] = mapped_column(String(40))
    confidence: Mapped[float] = mapped_column(Float)
    model_version: Mapped[str] = mapped_column(String(60))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    event: Mapped[Event] = relationship(back_populates="predictions")
    __table_args__ = (CheckConstraint("confidence >= 0 and confidence <= 1", name="ck_conf_range"),)


class RiskAssessment(Base):
    __tablename__ = "risk_assessments"
    id: Mapped[int] = mapped_column(primary_key=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id", ondelete="CASCADE"), index=True)
    impact: Mapped[float] = mapped_column(Float)
    urgency: Mapped[float] = mapped_column(Float)
    strategic_relevance: Mapped[float] = mapped_column(Float)
    evidence_quality: Mapped[float] = mapped_column(Float)
    overall_score: Mapped[float] = mapped_column(Float, index=True)
    priority: Mapped[str] = mapped_column(String(10), index=True)
    explanation: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    event: Mapped[Event] = relationship(back_populates="risk_assessments")
    __table_args__ = (
        CheckConstraint(
            "impact between 0 and 10 and urgency between 0 and 10 and "
            "strategic_relevance between 0 and 10 and evidence_quality between 0 and 10",
            name="ck_risk_components",
        ),
    )


class CompanyRelationship(Base):
    __tablename__ = "company_relationships"
    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), index=True)
    related_company_id: Mapped[int] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), index=True)
    relationship_type: Mapped[str] = mapped_column(String(20))
    verification_status: Mapped[str] = mapped_column(String(20), default="unverified")
    evidence_observation_id: Mapped[int | None] = mapped_column(ForeignKey("observations.id", ondelete="SET NULL"))
    __table_args__ = (
        UniqueConstraint("company_id", "related_company_id", "relationship_type", name="uq_rel"),
        CheckConstraint("company_id != related_company_id", name="ck_rel_not_self"),
        CheckConstraint(
            "relationship_type in ('competitor','customer','supplier','partner','stakeholder','other')",
            name="ck_rel_type",
        ),
    )


class Report(Base):
    __tablename__ = "reports"
    id: Mapped[int] = mapped_column(primary_key=True)
    report_type: Mapped[str] = mapped_column(String(30), index=True)
    title: Mapped[str] = mapped_column(String(300))
    company_id: Mapped[int | None] = mapped_column(ForeignKey("companies.id", ondelete="SET NULL"))
    content_json: Mapped[dict] = mapped_column(JSON)
    content_markdown: Mapped[str] = mapped_column(Text)
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)


class Workflow(Base, TimestampMixin):
    __tablename__ = "workflows"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    company_ids: Mapped[list] = mapped_column(JSON, default=list)
    categories: Mapped[list] = mapped_column(JSON, default=list)
    min_priority: Mapped[str] = mapped_column(String(10), default="low")
    report_type: Mapped[str] = mapped_column(String(30), default="daily")
    schedules: Mapped[list["DeliverySchedule"]] = relationship(back_populates="workflow", cascade="all, delete-orphan")


class DeliverySchedule(Base, TimestampMixin):
    __tablename__ = "delivery_schedules"
    id: Mapped[int] = mapped_column(primary_key=True)
    workflow_id: Mapped[int] = mapped_column(ForeignKey("workflows.id", ondelete="CASCADE"), index=True)
    mode: Mapped[str] = mapped_column(String(10))  # daily | interval
    time_of_day: Mapped[str | None] = mapped_column(String(5))  # HH:MM
    interval_minutes: Mapped[int | None] = mapped_column(Integer)
    timezone: Mapped[str] = mapped_column(String(64), default="UTC")
    workflow: Mapped[Workflow] = relationship(back_populates="schedules")
    recipients: Mapped[list["DeliveryRecipient"]] = relationship(back_populates="schedule", cascade="all, delete-orphan")
    __table_args__ = (CheckConstraint("mode in ('daily','interval')", name="ck_sched_mode"),)


class DeliveryRecipient(Base):
    __tablename__ = "delivery_recipients"
    id: Mapped[int] = mapped_column(primary_key=True)
    schedule_id: Mapped[int] = mapped_column(ForeignKey("delivery_schedules.id", ondelete="CASCADE"), index=True)
    channel: Mapped[str] = mapped_column(String(10))  # email | whatsapp
    address: Mapped[str] = mapped_column(String(300))
    authorized: Mapped[bool] = mapped_column(Boolean, default=False)
    schedule: Mapped[DeliverySchedule] = relationship(back_populates="recipients")


class DeliveryLog(Base):
    __tablename__ = "delivery_logs"
    id: Mapped[int] = mapped_column(primary_key=True)
    schedule_id: Mapped[int | None] = mapped_column(ForeignKey("delivery_schedules.id", ondelete="SET NULL"))
    report_id: Mapped[int | None] = mapped_column(ForeignKey("reports.id", ondelete="SET NULL"))
    channel: Mapped[str] = mapped_column(String(10))
    recipient: Mapped[str] = mapped_column(String(300))
    provider: Mapped[str] = mapped_column(String(30))
    status: Mapped[str] = mapped_column(String(20))  # simulated | sent | failed
    detail: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)


class UserSettings(Base):
    __tablename__ = "user_settings"
    id: Mapped[int] = mapped_column(primary_key=True)
    timezone: Mapped[str] = mapped_column(String(64), default="UTC")
    display_name: Mapped[str | None] = mapped_column(String(120))
    show_demo_data: Mapped[bool] = mapped_column(Boolean, default=True)


class Feedback(Base):
    __tablename__ = "feedback"
    id: Mapped[int] = mapped_column(primary_key=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id", ondelete="CASCADE"), index=True)
    correct_category: Mapped[str | None] = mapped_column(String(40))
    useful: Mapped[bool | None] = mapped_column(Boolean)
    comment: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


Index("ix_obs_company_collected", Observation.company_id, Observation.collected_at)
