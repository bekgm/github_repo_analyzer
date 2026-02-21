"""
Celery application instance.

Using a separate module so that `celery -A app.infrastructure.jobs.celery_app worker`
discovers the app without importing FastAPI.
"""

from celery import Celery

from app.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "github_analyzer",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,                # Re-deliver if worker crashes
    worker_prefetch_multiplier=1,       # Fair scheduling
    task_soft_time_limit=300,           # 5 min soft limit
    task_time_limit=360,                # 6 min hard kill
    result_expires=86400,               # Results expire after 24 h
)

celery_app.autodiscover_tasks(["app.infrastructure.jobs"])
