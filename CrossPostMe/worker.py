import os

from celery import Celery
from dotenv import load_dotenv

load_dotenv()

# Create Celery instance
celery_app = Celery(
    "crosspostme_worker",
    broker=os.environ.get("REDIS_URL", "redis://localhost:6379"),
    backend=os.environ.get("REDIS_URL", "redis://localhost:6379"),
    include=["tasks"],
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_routes={
        "tasks.process_social_post": {"queue": "social_posts"},
        "tasks.schedule_post": {"queue": "scheduler"},
        "tasks.validate_platforms": {"queue": "validation"},
    },
)

if __name__ == "__main__":
    celery_app.start()
