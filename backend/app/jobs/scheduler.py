"""Small in-process APScheduler integration for local development.

The scheduler is deliberately opt-in. API-triggered workflow execution remains
available even when no scheduler is started.
"""
from apscheduler.schedulers.background import BackgroundScheduler

_scheduler: BackgroundScheduler | None = None


def get_scheduler() -> BackgroundScheduler:
    global _scheduler
    if _scheduler is None:
        _scheduler = BackgroundScheduler()
    return _scheduler


def start_scheduler() -> BackgroundScheduler:
    scheduler = get_scheduler()
    if not scheduler.running:
        scheduler.start()
    return scheduler


def stop_scheduler() -> None:
    global _scheduler
    if _scheduler and _scheduler.running:
        _scheduler.shutdown(wait=False)
    _scheduler = None
