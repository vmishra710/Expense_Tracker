from celery import Celery

celery_app = Celery(
    'expense_tracker',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/1',
    include=['tasks.email_tasks']
)

celery_app.conf.update(
    task_track_started=True,
    result_expires=3600
)

