from celery import Celery
from app.config import settings

celery_app = Celery("kenyaads", broker=settings.redis_url, backend=settings.redis_url, include=["app.worker.tasks"])
celery_app.conf.update(task_serializer="json", accept_content=["json"], result_serializer="json", timezone="Africa/Nairobi", enable_utc=True, result_expires=3600)
