from fastapi import APIRouter, HTTPException
from starlette import status
from dependencies import db_dependency, user_dependency
from models import Expense

router = APIRouter(
    prefix="/admin",
    tags=["admin"]
)

@router.get("/expenses", status_code=status.HTTP_200_OK)
async def read_all_expenses(db : db_dependency,
                            user : user_dependency):
    if user is None or user.get('role') != 'admin' :
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Admins only : access denied.')
    expenses = db.query(Expense).all()
    return expenses

@router.delete("/expenses/{expense_id}", status_code=status.HTTP_200_OK)
async def delete_expense(expense_id : int,
                         db : db_dependency,
                         user : user_dependency):
    if user is None or user.get('role') != 'admin' :
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Admins only : access denied.')

    expense = db.query(Expense).filter_by(id=expense_id).first()
    if expense is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Expense not found')

    db.delete(expense)
    db.commit()
    return {"message" : f"Expense {expense_id} deleted successfully"}