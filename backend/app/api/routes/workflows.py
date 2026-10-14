from fastapi import APIRouter, Depends, Response
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import PageParams
from app.core.database import get_db
from app.models import DeliveryLog, DeliveryRecipient, DeliverySchedule, Workflow
from app.schemas import (
    DeliveryLogOut,
    Page,
    RecipientIn,
    RecipientOut,
    ScheduleIn,
    ScheduleOut,
    WorkflowIn,
    WorkflowOut,
    WorkflowPatch,
)
from app.services.companies import NotFoundError
from app.services.workflows import (
    add_recipient,
    add_schedule,
    create_workflow,
    execute_workflow,
    update_workflow,
)

router = APIRouter(tags=["workflows"])


def _workflow(db: Session, workflow_id: int) -> Workflow:
    row = db.get(Workflow, workflow_id)
    if not row:
        raise NotFoundError(f"Workflow {workflow_id} not found")
    return row


@router.get("/workflows", response_model=Page[WorkflowOut])
def list_workflows(p: PageParams = Depends(), db: Session = Depends(get_db)):
    stmt = select(Workflow)
    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    rows = db.scalars(stmt.order_by(Workflow.id).offset(p.offset).limit(p.limit)).all()
    return Page(items=rows, total=total, offset=p.offset, limit=p.limit)


@router.post("/workflows", response_model=WorkflowOut, status_code=201)
def post_workflow(body: WorkflowIn, db: Session = Depends(get_db)):
    return create_workflow(db, **body.model_dump())


@router.get("/workflows/{workflow_id}", response_model=WorkflowOut)
def get_workflow(workflow_id: int, db: Session = Depends(get_db)):
    return _workflow(db, workflow_id)


@router.patch("/workflows/{workflow_id}", response_model=WorkflowOut)
def patch_workflow(workflow_id: int, body: WorkflowPatch, db: Session = Depends(get_db)):
    return update_workflow(db, _workflow(db, workflow_id), **body.model_dump(exclude_unset=True))


@router.delete("/workflows/{workflow_id}", status_code=204)
def delete_workflow(workflow_id: int, db: Session = Depends(get_db)):
    db.delete(_workflow(db, workflow_id))
    db.commit()
    return Response(status_code=204)


@router.get("/workflows/{workflow_id}/schedules", response_model=list[ScheduleOut])
def list_schedules(workflow_id: int, db: Session = Depends(get_db)):
    _workflow(db, workflow_id)
    return db.scalars(select(DeliverySchedule).where(DeliverySchedule.workflow_id == workflow_id).order_by(DeliverySchedule.id)).all()


@router.post("/workflows/{workflow_id}/schedules", response_model=ScheduleOut, status_code=201)
def post_schedule(workflow_id: int, body: ScheduleIn, db: Session = Depends(get_db)):
    return add_schedule(db, workflow_id=workflow_id, **body.model_dump())


@router.get("/schedules/{schedule_id}/recipients", response_model=list[RecipientOut])
def list_recipients(schedule_id: int, db: Session = Depends(get_db)):
    if not db.get(DeliverySchedule, schedule_id):
        raise NotFoundError(f"Schedule {schedule_id} not found")
    return db.scalars(select(DeliveryRecipient).where(DeliveryRecipient.schedule_id == schedule_id).order_by(DeliveryRecipient.id)).all()


@router.post("/schedules/{schedule_id}/recipients", response_model=RecipientOut, status_code=201)
def post_recipient(schedule_id: int, body: RecipientIn, db: Session = Depends(get_db)):
    return add_recipient(db, schedule_id=schedule_id, **body.model_dump())


@router.post("/workflows/{workflow_id}/execute")
def execute(workflow_id: int, db: Session = Depends(get_db)):
    return execute_workflow(db, _workflow(db, workflow_id))


@router.get("/delivery-logs", response_model=Page[DeliveryLogOut])
def list_delivery_logs(p: PageParams = Depends(), db: Session = Depends(get_db)):
    stmt = select(DeliveryLog)
    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    rows = db.scalars(stmt.order_by(DeliveryLog.created_at.desc(), DeliveryLog.id.desc()).offset(p.offset).limit(p.limit)).all()
    return Page(items=rows, total=total, offset=p.offset, limit=p.limit)


@router.get("/notification-providers")
def notification_providers():
    return {
        "providers": [
            {
                "name": "mock",
                "channels": ["email", "whatsapp"],
                "status": "available",
                "detail": "Development-only provider. It records delivery logs and sends no real messages.",
            }
        ]
    }
