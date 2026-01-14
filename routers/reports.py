from datetime import date

from fastapi import APIRouter, HTTPException, status
from dependencies import db_dependency, user_dependency
from models import User
from tasks.email_tasks import send_monthly_expense_report

router = APIRouter(
    prefix="/reports",
    tags=["reports"]
)

@router.post("/run-monthly", status_code = status.HTTP_202_ACCEPTED)
async def run_monthly_reports(
        db : db_dependency,
        user : user_dependency
):

    if user["role"] != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Admin access required")

    today = date.today()
    year = today.year
    month = today.month

    users = db.query(User).all()

    if not users:
        return {"message": "No users found"}

    # Queue one task per user
    for u in users:
        send_monthly_expense_report.delay(
            user_id = u.id,
            year = year,
            month = month
        )

    return {
        "message" : "Monthly expense reports queued",
        "users_processes" : len(users),
        "month" : f"{month}/{year}"
    }