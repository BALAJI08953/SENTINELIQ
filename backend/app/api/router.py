from fastapi import APIRouter

from app.api.routes import analytics, companies, events

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(analytics.router)
api_router.include_router(companies.router)
api_router.include_router(events.router)
