from datetime import date
from fastapi import APIRouter, HTTPException, Path, Query
from pydantic import BaseModel, Field
from sqlalchemy import text
from starlette import status

from dependencies import user_dependency, db_dependency
from models import Expense

router = APIRouter(
    prefix='/expenses',
    tags=['expenses']
)

class CreateExpenseRequest(BaseModel):
    amount : int = Field(gt=0)
    category : str
    description : str

class UpdatedExpense(BaseModel):
    amount : int = Field(gt=0)
    category : str
    description : str

@router.post('/new_expense', status_code = status.HTTP_201_CREATED)
async def create_expense(request : CreateExpenseRequest,
                         user : user_dependency,
                         db : db_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid User')
    expense_model = Expense(
        amount = request.amount,
        category = request.category,
        description = request.description,
        owner_id = user.get('id')
    )
    db.add(expense_model)
    db.commit()
    db.refresh(expense_model)
    return expense_model

@router.get('/my_expenses', status_code = status.HTTP_200_OK)
async def get_expenses(user : user_dependency, db : db_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid User')
    expenses = db.query(Expense).filter_by(owner_id=user.get('id')).all()
    return expenses

@router.put('/update_expense/{expense_id}', status_code = status.HTTP_201_CREATED)
async def update_expenses(request : UpdatedExpense,
                          user : user_dependency, db : db_dependency,
                          expense_id : int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid User')

    expense_model = db.query(Expense).filter_by(owner_id = user.get('id')).filter_by(id=expense_id).first()
    if expense_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Expense Not Found')

    expense_model.amount = request.amount
    expense_model.category=request.category
    expense_model.description=request.description

    db.add(expense_model)
    db.commit()
    db.refresh(expense_model)
    return expense_model

@router.delete('/delete_expense/{expense_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_expense(expense_id : int, db : db_dependency, user:user_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid User')

    expense_model = db.query(Expense).filter_by(owner_id=user.get('id')).filter_by(id=expense_id).first()
    if expense_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Invalid Expense Id')
    db.delete(expense_model)
    db.commit()
    return {'message' : 'Expense deleted Successfully'}


@router.get('/summary', status_code = status.HTTP_200_OK)
async def get_expense_summary(db : db_dependency, user : user_dependency):
    query = text("""
        SELECT category, SUM(amount) AS total_spent
        FROM expenses
        WHERE owner_id = :owner_id
        GROUP BY category
        ORDER BY total_spent DESC
    """)
    result = db.execute(query, {'owner_id':user.get('id')})
    return [{'category' : row[0], 'total_spent' : row[1]} for row in result.fetchall()]

@router.get('/filter_expenses', status_code = status.HTTP_200_OK)
async def filter_expenses(db : db_dependency, user : user_dependency,
                          start_date : date = Query(...,description='Start Date in YYYY-MM-DD'),
                          end_date : date = Query(...,description='End Date in YYYY-MM-DD')):
    query = text("""
        SELECT id, amount, category, description, date
        FROM expenses
        Where owner_id = :owner_id
        AND date BETWEEN :start_date AND :end_date
        ORDER BY date ASC
    """)

    result = db.execute(query,{
        'owner_id' : user.get('id'),
        'start_date' : start_date,
        'end_date' : end_date
    })

    return [{
        'id' : row[0],
        'amount' : row[1],
        'category' : row[2],
        'description' : row[3],
        'date' : row[3]
    }  for row in result.fetchall()]


@router.get('/top_categories', status_code=status.HTTP_200_OK)
async def top_spending_categories(db : db_dependency, user : user_dependency,
                                  top_limit : int = Query(..., description='Top N Spend Categories')):
    query = text("""
        SELECT category, SUM(amount) AS total_spent
        FROM expenses
        WHERE owner_id = :owner_id
        GROUP BY category
        ORDER BY total_spent DESC
        LIMIT :top_limit
    """)

    result = db.execute(query, {
        'owner_id' : user.get('id'), 'top_limit' : top_limit
    })

    return [{
        'category' : row[0], 'total_spent' : row[1]
    } for row in result.fetchall()]
