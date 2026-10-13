from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.router import api_router
from app.ml.predict import ModelNotAvailableError
from app.services.companies import ConflictError, NotFoundError


def create_app() -> FastAPI:
    app = FastAPI(title="SentinelIQ API", version="0.1.0",
                  description="Competitive intelligence. Demo records are fictional and flagged is_demo.")
    app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
                       allow_methods=["*"], allow_headers=["*"])

    def err(status: int, code: str):
        async def handler(_: Request, exc: Exception):
            return JSONResponse(status_code=status, content={"error": {"code": code, "message": str(exc)}})
        return handler

    app.add_exception_handler(NotFoundError, err(404, "not_found"))
    app.add_exception_handler(ConflictError, err(409, "conflict"))
    app.add_exception_handler(ValueError, err(422, "invalid_request"))
    app.add_exception_handler(ModelNotAvailableError, err(503, "model_unavailable"))
    app.include_router(api_router)
    return app


app = create_app()
