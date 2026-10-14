import json

from fastapi import APIRouter, Depends, Response
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import PageParams
from app.core.database import get_db
from app.models import Report
from app.schemas import Page, ReportCreate, ReportOut
from app.services.companies import NotFoundError
from app.services.reports import create_company_report

router = APIRouter(tags=["reports"])


def _report(db: Session, report_id: int) -> Report:
    row = db.get(Report, report_id)
    if not row:
        raise NotFoundError(f"Report {report_id} not found")
    return row


@router.post("/reports", response_model=ReportOut, status_code=201)
def create_report(body: ReportCreate, db: Session = Depends(get_db)):
    if body.start and body.end and body.start > body.end:
        raise ValueError("start must be before end")
    return create_company_report(db, body.company_id, body.start, body.end)


@router.get("/reports", response_model=Page[ReportOut])
def list_reports(company_id: int | None = None, p: PageParams = Depends(), db: Session = Depends(get_db)):
    stmt = select(Report)
    if company_id:
        stmt = stmt.where(Report.company_id == company_id)
    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    rows = db.scalars(stmt.order_by(Report.created_at.desc(), Report.id.desc()).offset(p.offset).limit(p.limit)).all()
    return Page(items=rows, total=total, offset=p.offset, limit=p.limit)


@router.get("/reports/{report_id}", response_model=ReportOut)
def get_report(report_id: int, db: Session = Depends(get_db)):
    return _report(db, report_id)


@router.get("/reports/{report_id}/export")
def export_report(report_id: int, format: str = "markdown", db: Session = Depends(get_db)):
    row = _report(db, report_id)
    if format == "markdown":
        return Response(
            content=row.content_markdown,
            media_type="text/markdown",
            headers={"Content-Disposition": f'attachment; filename="sentineliq-report-{row.id}.md"'},
        )
    if format == "json":
        return Response(
            content=json.dumps(row.content_json, indent=2),
            media_type="application/json",
            headers={"Content-Disposition": f'attachment; filename="sentineliq-report-{row.id}.json"'},
        )
    raise ValueError("format must be 'markdown' or 'json'")
