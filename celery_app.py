import os
import ssl
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

celery_app.conf.broker_use_ssl = {"ssl_cert_reqs":"ssl.CERT_NONE"}
celery_app.conf.redis_backend_use_ssl = {"ssl_cert_reqs":"ssl.CERT_NONE"}

celery_app.conf.update(
    task_track_started=True,
    result_expires=3600
)

