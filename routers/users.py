
from fastapi import APIRouter, HTTPException
from starlette import status
from dependencies import db_dependency, user_dependency
from models import User

router = APIRouter(
    prefix='/user',
    tags=['user']
)

@router.get('/me', status_code=status.HTTP_200_OK)
async def get_user(user:user_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication Failed')
    return user

# @router.put('/password', status_code=)
# async def change_password():



