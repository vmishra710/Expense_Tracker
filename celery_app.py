from celery import Celery
import os

REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')

celery_app = Celery(
    'expense_tracker',
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=['tasks.email_tasks']
)

celery_app.conf.update(
    task_track_started=True,
    result_expires=3600
)

