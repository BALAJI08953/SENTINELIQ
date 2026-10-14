from fastapi import APIRouter

from app.api.routes import analytics, companies, events, insights, ml, reports, sentrix, workflows

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(analytics.router)
api_router.include_router(companies.router)
api_router.include_router(events.router)
api_router.include_router(insights.router)
api_router.include_router(ml.router)
api_router.include_router(reports.router)
api_router.include_router(workflows.router)
api_router.include_router(sentrix.router)
