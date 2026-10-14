from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import (
    Company,
    DeliveryLog,
    DeliveryRecipient,
    DeliverySchedule,
    Report,
    Workflow,
)
from app.services.companies import NotFoundError
from app.services.reports import create_company_report

PRIORITIES = {"low", "medium", "high", "critical"}


def validate_workflow(name: str, min_priority: str, report_type: str) -> None:
    if not name.strip():
        raise ValueError("name is required")
    if min_priority not in PRIORITIES:
        raise ValueError("min_priority must be low, medium, high, or critical")
    if report_type not in {"daily", "weekly", "company", "high_priority"}:
        raise ValueError("report_type must be daily, weekly, company, or high_priority")


def create_workflow(
    db: Session,
    name: str,
    enabled: bool = True,
    company_ids: list[int] | None = None,
    categories: list[str] | None = None,
    min_priority: str = "low",
    report_type: str = "daily",
) -> Workflow:
    validate_workflow(name, min_priority, report_type)
    for company_id in company_ids or []:
        if not db.get(Company, company_id):
            raise NotFoundError(f"Company {company_id} not found")
    row = Workflow(
        name=name.strip(),
        enabled=enabled,
        company_ids=company_ids or [],
        categories=categories or [],
        min_priority=min_priority,
        report_type=report_type,
    )
    db.add(row)
    db.commit()
    return row


def update_workflow(db: Session, workflow: Workflow, **fields) -> Workflow:
    data = {k: v for k, v in fields.items() if v is not None}
    validate_workflow(
        str(data.get("name", workflow.name)),
        str(data.get("min_priority", workflow.min_priority)),
        str(data.get("report_type", workflow.report_type)),
    )
    for company_id in data.get("company_ids", workflow.company_ids) or []:
        if not db.get(Company, company_id):
            raise NotFoundError(f"Company {company_id} not found")
    for key, value in data.items():
        setattr(workflow, key, value.strip() if key == "name" and isinstance(value, str) else value)
    db.commit()
    return workflow


def add_schedule(
    db: Session,
    workflow_id: int,
    mode: str,
    timezone: str,
    time_of_day: str | None = None,
    interval_minutes: int | None = None,
) -> DeliverySchedule:
    if mode not in {"daily", "interval"}:
        raise ValueError("mode must be daily or interval")
    if mode == "daily" and not time_of_day:
        raise ValueError("daily schedules require time_of_day")
    if mode == "interval" and (interval_minutes is None or interval_minutes < 1):
        raise ValueError("interval schedules require interval_minutes >= 1")
    if not db.get(Workflow, workflow_id):
        raise NotFoundError(f"Workflow {workflow_id} not found")
    row = DeliverySchedule(
        workflow_id=workflow_id,
        mode=mode,
        time_of_day=time_of_day,
        interval_minutes=interval_minutes,
        timezone=timezone,
    )
    db.add(row)
    db.commit()
    return row


def add_recipient(db: Session, schedule_id: int, channel: str, address: str, authorized: bool = False) -> DeliveryRecipient:
    if channel not in {"email", "whatsapp"}:
        raise ValueError("channel must be email or whatsapp")
    if not address.strip():
        raise ValueError("address is required")
    if not db.get(DeliverySchedule, schedule_id):
        raise NotFoundError(f"Schedule {schedule_id} not found")
    row = DeliveryRecipient(schedule_id=schedule_id, channel=channel, address=address.strip(), authorized=authorized)
    db.add(row)
    db.commit()
    return row


def execute_workflow(db: Session, workflow: Workflow) -> dict:
    company_ids = list(workflow.company_ids or [])
    if not company_ids:
        first_company = db.scalar(select(Company).order_by(Company.id).limit(1))
        if not first_company:
            raise ValueError("No companies exist for report generation")
        company_ids = [first_company.id]
    reports: list[Report] = []
    for company_id in company_ids:
        reports.append(create_company_report(db, company_id))
    schedules = db.scalars(select(DeliverySchedule).where(DeliverySchedule.workflow_id == workflow.id)).all()
    logs: list[DeliveryLog] = []
    for schedule in schedules:
        recipients = db.scalars(select(DeliveryRecipient).where(DeliveryRecipient.schedule_id == schedule.id)).all()
        for recipient in recipients:
            for report in reports:
                status = "simulated" if recipient.authorized else "failed"
                detail = (
                    "Mock provider recorded a simulated delivery; no real message was sent."
                    if recipient.authorized
                    else "Recipient is not authorized for delivery."
                )
                log = DeliveryLog(
                    schedule_id=schedule.id,
                    report_id=report.id,
                    channel=recipient.channel,
                    recipient=recipient.address,
                    provider="mock",
                    status=status,
                    detail=detail,
                )
                db.add(log)
                logs.append(log)
    db.commit()
    return {
        "workflow_id": workflow.id,
        "reports_created": len(reports),
        "delivery_logs_created": len(logs),
        "simulated": sum(1 for log in logs if log.status == "simulated"),
        "failed": sum(1 for log in logs if log.status == "failed"),
    }
