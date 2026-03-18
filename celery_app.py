import os
from celery import Celery
from dotenv import load_dotenv
load_dotenv()

REDIS_URL = os.getenv('REDIS_URL')

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

