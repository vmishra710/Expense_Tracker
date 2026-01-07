from fastapi import APIRouter
from dependencies import user_dependency
from tasks.email_tasks import send_monthly_expense_report

router = APIRouter(
    prefix="/reports",
    tags=["reports"]
)

@router.post("/monthly-expense-report")
async def send_monthly_report(user : user_dependency):
    send_monthly_expense_report.delay(
        user_id = user["id"],
        email = user["email"]
    )
    return {"message" : "Monthly expense report scheduled"}