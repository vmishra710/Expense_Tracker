import datetime
from datetime import date
from typing import Optional
from fastapi import APIRouter, HTTPException, Path, Query
from pydantic import BaseModel, Field
from sqlalchemy import text, select, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload
from starlette import status
from dependencies import user_dependency, db_dependency, async_db_dependency
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


async def get_or_create_category_async(db, user_id : int, name : str) -> Category:
    name = name.strip()

    # Try to find existing
    result = await db.execute(
        select(Category).filter_by(owner_id = user_id, name = name)
    )

    category = result.scalar_one_or_none()
    if category:
        return category

    # Create new
    category = Category(name = name, owner_id = user_id)
    db.add(category)

    try:
        # Commit and refresh
        await db.commit()
        await db.refresh(category)
        return category
    except IntegrityError:
        # Handle concurrent creation
        await db.rollback()
        result = await db.execute(select(Category).filter_by(owner_id = user_id, name = name))
        return result.scalar_one_or_none()


# @router.post('/new_expense', status_code = status.HTTP_201_CREATED)
# async def create_expense(request : CreateExpenseRequest,
#                          user : user_dependency,
#                          db : db_dependency):
#     if user is None:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid User')
#
#     #ensure category exists for this user or else create it
#     category = get_or_create_category(db, user.get('id'), request.category_name)
#
#     expense_model = Expense(
#         amount = request.amount,
#         category_id = category.id,
#         description = request.description,
#         owner_id = user.get('id')
#     )
#     db.add(expense_model)
#     db.commit()
#     db.refresh(expense_model)
#
#     return {
#         "id" : expense_model.id,
#         "amount" : expense_model.amount,
#         "description" : expense_model.description,
#         "category" : category.name,
#         "date" : expense_model.date
#     }

@router.post('/new_expense', status_code = status.HTTP_201_CREATED)
async def create_expense(request : CreateExpenseRequest,
                         user : user_dependency,
                         db : async_db_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid User')

    #ensure category exists for this user or else create it
    category = await get_or_create_category_async(db, user.get('id'), request.category_name)

    expense_model = Expense(
        amount = request.amount,
        category_id = category.id,
        description = request.description,
        owner_id = user.get('id')
    )
    db.add(expense_model)
    await db.commit()
    await db.refresh(expense_model)

    return {
        "id" : expense_model.id,
        "amount" : expense_model.amount,
        "description" : expense_model.description,
        "category" : category.name,
        "date" : expense_model.date
    }


# @router.get('/my_expenses', status_code = status.HTTP_200_OK)
# async def get_expenses(user : user_dependency,
#                        db : db_dependency,
#                        limit : int = Query(5, ge=0, le=50, description='Number of expenses to return'),
#                        offset : int = Query(0, ge=0, description='Number of expenses to skip')
#                        ):
#     if user is None:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid User')
#
#     total_count = db.query(Expense).filter_by(owner_id=user.get('id')).count()
#
#     expenses = db.query(Expense)\
#         .filter_by(owner_id=user.get('id'))\
#         .order_by(Expense.date.desc())\
#         .offset(offset)\
#         .limit(limit)\
#         .all()
#
#     response = [
#         {
#             "id" : e.id,
#             "amount" : e.amount,
#             "description" : e.description,
#             "category" : e.category.name if e.category else None,
#             "date" : e.date
#         } for e in expenses
#     ]
#
#     return paginate_query_result(response, total_count, limit, offset)

@router.get('/my_expenses', status_code = status.HTTP_200_OK)
async def get_expenses(user : user_dependency,
                       db : async_db_dependency,
                       limit : int = Query(5, ge=0, le=50, description='Number of expenses to return'),
                       offset : int = Query(0, ge=0, description='Number of expenses to skip')
                       ):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid User')

    count_query = select(func.count(Expense.id)).filter_by(owner_id=user.get('id'))
    total_result = await db.execute(count_query)
    total_count = total_result.scalar() or 0

    expenses_query = (
        select(Expense)
        .options(selectinload(Expense.category))
        .filter_by(owner_id=user.get('id'))
        .order_by(Expense.date.desc())
        .offset(offset)
        .limit(limit)
    )
    result = await db.execute(expenses_query)
    expenses = result.scalars().all()

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

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid User')

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

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid User')

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
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid User')

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


@router.put('/bulk_update_category', status_code=status.HTTP_200_OK)
async def bulk_update_category(db : db_dependency,
                               user : user_dependency,
                               old_category : str,
                               new_category : str):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid User')

    old_name = old_category.strip()
    new_name = new_category.strip()

    if old_name.lower() == new_name.lower():
        return {'message' : 'Old and New category are the same; nothing to do.'}

    #finding existing old category
    old = db.query(Category).filter_by(owner_id=user.get('id'), name=old_name).first()
    if not old:
        return {'message' : f'No category name {old_name} found for this user.', 'updated':0}

    #ensure new category exists
    new = get_or_create_category(db, user.get('id'), new_name)

    now = datetime.datetime.now(datetime.timezone.utc)
    bulk_update_query = text("""
        UPDATE expenses
        SET category_id = :new_cid, updated_at = :now
        WHERE category_id = :old_cid AND owner_id = :owner_id
        RETURNING id
    """)

    try:
        result = db.execute(bulk_update_query, {
            'new_cid': new.id,
            'old_cid': old.id,
            'owner_id': user.get('id'),
            'now': now
        })
        updated_rows = [r[0] for r in result.fetchall()]
        db.commit()

    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update expenses : {str(exc)}")

    return {
        'message' : f"{len(updated_rows)} expenses moved from '{old_name}' to '{new_name}'.",
        'updated_count' : len(updated_rows),
        'updated_ids' : updated_rows,
        'from_category_id' : old.id,
        'to_category_id' : new.id
    }

@router.delete('/bulk_delete_expenses', status_code=status.HTTP_200_OK)
async def bulk_delete_expenses(db : db_dependency,
                               user : user_dependency,
                               category_names : list[int]):

    """
    Delete multiple expenses by category_name for a user
    Rollback if any issue occurs
    """

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid User')


    # Resolve category names -> ids
    categories = db.query(Category).filter(
        Category.owner_id == user.get('id'),
        Category.name.in_([name.strip() for name in category_names])
    ).all()

    if not categories:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No matching categories found for this user.')

    category_ids = [c.id for c in categories]

    try:
        bulk_delete_query = """
            DELETE FROM expenses
            WHERE user_id = :user_id AND category_id in :category_ids
            RETURNING id
        """

        result = db.execute(bulk_delete_query , {
            'user_id' : user.get('id'),
            'category_ids' : tuple(category_ids)
        })

        deleted_ids = [r[0] for r in result.fetchall()]
        db.commit()
        return {
            'message' : f'Deleted {len(deleted_ids)} expenses under categories : {category_names}',
            'deleted_ids' : deleted_ids,
            'categories_resolved' : {c.name : c.id for c in categories}
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f'Rollback due to error : {str(e)}')




















