"""Public health/status endpoint (used by the login page and the status badge)."""

from fastapi import APIRouter, Request

from app.config import get_settings
from app.schemas import SystemStatus

router = APIRouter(prefix="/system", tags=["system"])


@router.get("/status", response_model=SystemStatus)
def system_status(request: Request):
    settings = get_settings()
    worker = request.app.state.worker
    return SystemStatus(
        engine=worker.engine.name,
        engine_ready=worker.ready,
        engine_error=worker.error,
        model_id=settings.model_id,
        queue_length=worker.queue_length(),
        allow_registration=settings.allow_registration,
        update=worker.updater.info,
    )
