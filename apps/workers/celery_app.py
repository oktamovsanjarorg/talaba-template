from celery import Celery
from core.config import settings

celery_app = Celery(
    "talaba_workers",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["apps.workers.tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Tashkent",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300, # 5 daqiqa maksimal
    worker_prefetch_multiplier=1, # Adolatli navbat
    beat_schedule={
        # Har kuni ertalab 07:30 da dars jadvali va deadline tekshiruvi
        "check-hemis-deadlines-every-morning": {
            "task": "apps.workers.tasks.check_all_hemis_deadlines",
            "schedule": 3600.0, # Har soatda tekshirish
        },
    }
)
