from datetime import date
from typing import Optional

from fastapi import APIRouter, HTTPException, Path, Query
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from starlette import status
from dependencies import user_dependency, db_dependency
from models import Expense, Category
from pagination import paginate_query_result

router = APIRouter(
    prefix='/expenses',
    tags=['expenses']
)

class CreateExpenseRequest(BaseModel):
    amount : float = Field(gt=0)
    category_name : str
    description : Optional[str] = None

class UpdatedExpense(BaseModel):
    amount : float = Field(gt=0)
    category_name : str
    description : Optional[str] = None

def get_or_create_category(db, user_id : int, name : str) -> Category:
    name = name.strip()

    #try to find existing
    category = db.query(Category).filter_by(owner_id = user_id, name = name).first()
    if category:
        return category

    #create new
    category = Category(name = name, owner_id = user_id)
    db.add(category)

    try:
        db.commit()
        db.refresh(category)
        return category
    except IntegrityError:
        #concurrent create -> rollback and re-fetch
        db.rollback()
        return db.query(Category).filter_by(owner_id = user_id, name = name).first()


@router.post('/new_expense', status_code = status.HTTP_201_CREATED)
async def create_expense(request : CreateExpenseRequest,
                         user : user_dependency,
                         db : db_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid User')

    #ensure category exists for this user or else create it
    category = get_or_create_category(db, user.get('id'), request.category_name)

    expense_model = Expense(
        amount = request.amount,
        category_id = category.id,
        description = request.description,
        owner_id = user.get('id')
    )
    db.add(expense_model)
    db.commit()
    db.refresh(expense_model)

    return {
        "id" : expense_model.id,
        "amount" : expense_model.amount,
        "description" : expense_model.description,
        "category" : category.name,
        "date" : expense_model.date
    }

@router.get('/my_expenses', status_code = status.HTTP_200_OK)
async def get_expenses(user : user_dependency,
                       db : db_dependency,
                       limit : int = Query(5, ge=0, le=50, description='Number of expenses to return'),
                       offset : int = Query(0, ge=0, description='Number of expenses to skip')
                       ):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid User')

    total_count = db.query(Expense).filter_by(owner_id=user.get('id')).count()

    expenses = db.query(Expense)\
        .filter_by(owner_id=user.get('id'))\
        .order_by(Expense.date.desc())\
        .offset(offset)\
        .limit(limit)\
        .all()

    response = [
        {
            "id" : e.id,
            "amount" : e.amount,
            "description" : e.description,
            "category" : e.category.name if e.category else None,
            "date" : e.date
        } for e in expenses
    ]

    return paginate_query_result(response, total_count, limit, offset)

@router.put('/update_expense/{expense_id}', status_code = status.HTTP_201_CREATED)
async def update_expenses(request : UpdatedExpense,
                          user : user_dependency, db : db_dependency,
                          expense_id : int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid User')

    expense_model = db.query(Expense).filter_by(owner_id = user.get('id')).filter_by(id=expense_id).first()
    if expense_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Expense Not Found')

    category = get_or_create_category(db, user.get('id'), request.category_name)

    expense_model.amount = request.amount
    expense_model.category_id=category.id
    expense_model.description=request.description

    db.add(expense_model)
    db.commit()
    db.refresh(expense_model)
    return {
        "id": expense_model.id,
        "amount": expense_model.amount,
        "description": expense_model.description,
        "category": category.name,
        "date": expense_model.date
    }

@router.delete('/delete_expense/{expense_id}', status_code=status.HTTP_200_OK)
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
        SELECT c.name AS category, SUM(e.amount) AS total_spent
        FROM expenses e
        JOIN categories c ON e.category_id = c.id
        WHERE e.owner_id = :owner_id
        GROUP BY c.name
        ORDER BY total_spent DESC
    """)

    result = db.execute(query, {'owner_id':user.get('id')})
    return [{'category' : row[0], 'total_spent' : row[1]} for row in result.fetchall()]

@router.get('/filter_expenses', status_code = status.HTTP_200_OK)
async def filter_expenses(db : db_dependency,
                          user : user_dependency,
                          start_date : date = Query(...,description='Start Date in YYYY-MM-DD'),
                          end_date : date = Query(...,description='End Date in YYYY-MM-DD'),
                          limit : int = Query(5, ge=1, le=50, description='Number of expenses to return'),
                          offset : int = Query(0, ge=0, description='Number of expenses to skip')):

    count_query = text("""
        SELECT COUNT(*) 
        FROM expenses
        WHERE owner_id = :owner_id
        AND date BETWEEN :start_date AND :end_date
    """)
    count_result = db.execute(count_query, {
        'owner_id': user.get('id'),
        'start_date': start_date,
        'end_date': end_date
    })
    total_count = count_result.scalar()

    data_query = text("""
        SELECT e.id, e.amount, c.name, e.description, e.date
        FROM expenses e
        JOIN categories c ON e.category_id = c.id
        Where e.owner_id = :owner_id
        AND e.date BETWEEN :start_date AND :end_date
        ORDER BY e.date ASC
        LIMIT :limit 
        OFFSET :offset
    """)

    result = db.execute(data_query,{
        'owner_id' : user.get('id'),
        'start_date' : start_date,
        'end_date' : end_date,
        'limit' : limit,
        'offset' : offset
    })

    expenses = [
        {
            'id': row[0],
            'amount': row[1],
            'category': row[2],
            'description': row[3],
            'date': row[4]
        } for row in result.fetchall()
    ]

    return paginate_query_result(expenses, total_count, limit, offset)


@router.get('/top_categories', status_code=status.HTTP_200_OK)
async def top_spending_categories(db : db_dependency, user : user_dependency,
                                  top_limit : int = Query(..., description='Top N Spend Categories')):
    query = text("""
        SELECT c.name AS category, SUM(e.amount) AS total_spent
        FROM expenses e
        JOIN categories c ON e.category_id = c.id
        WHERE e.owner_id = :owner_id
        GROUP BY c.name
        ORDER BY total_spent DESC
        LIMIT :top_limit
    """)

    result = db.execute(query, {
        'owner_id' : user.get('id'), 'top_limit' : top_limit
    })

    return [{
        'category' : row[0], 'total_spent' : row[1]
    } for row in result.fetchall()]
