# celery_app.py
from celery import Celery
import os
from dotenv import load_dotenv

load_dotenv()

# Celery configuration
celery = Celery(
    "ocean_hazard_tasks",
    broker=os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0"),
    include=["tasks.social_media", "tasks.nlp", "tasks.hotspots"]
)

# Optional configuration
celery.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
)

if __name__ == "__main__":
    celery.start()
