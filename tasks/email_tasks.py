import logging
import datetime
from database import SessionLocal
from services.report_service import (
    get_monthly_expense_summary,
    build_monthly_report_html
)
from celery_app import celery_app
from send_email import send_email
from tasks.exceptions import RetryableEmailError

logger = logging.getLogger(__name__)

@celery_app.task(bind=True,
                 autoretry_for=(RetryableEmailError,),
                 retry_backoff = True,
                 retry_kwargs = {"max_retries" : 5},
                 retry_jitter = True,
                 acks_late=True)
def send_monthly_expense_report(self, user_id : int, email : str):
    db = SessionLocal()
    try:
        now = datetime.datetime.now(datetime.timezone.utc)
        year = now.year
        month = now.month

        summary = get_monthly_expense_summary(
            db = db,
            user_id = user_id,
            year = year,
            month = month
        )

        html_body = build_monthly_report_html(summary, year, month)

        send_email(
            to_email = email,
            subject = "📊 Your Monthly Expense Report",
            html_body = html_body
        )

    except Exception as exc:
        logger.exception(
            f"Monthly report failed | user_id={user_id} | {month}/{year}"
        )
        raise #why raise again? Celery must see the exception otherwise no retry, task marked as success

    finally:
        db.close()