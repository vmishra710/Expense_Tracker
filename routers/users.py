from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from starlette import status
from dependencies import db_dependency, user_dependency
from models import User
from security import verify_password, hash_password

router = APIRouter(
    prefix='/user',
    tags=['user']
)

class UserVerification(BaseModel):
    old_password : str
    new_password : str = Field(min_length = 8)

class DeleteProfileRequest(BaseModel):
    userPassword : str

@router.get('/me', status_code=status.HTTP_200_OK)
async def get_user(user:user_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication Failed')
    return user

@router.put('/password', status_code=status.HTTP_201_CREATED)
async def change_password(request : UserVerification,
                          db : db_dependency, user : user_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid User')
    user_model = db.query(User).filter_by(id=user.get('id')).first()
    if verify_password(request.old_password, user_model.hashed_password):
        user_model.hashed_password = hash_password(request.new_password)
    db.add(user_model)
    db.commit()
    return {'message' : 'Password Updated Successfully'}

@router.delete('/delete_profile', status_code=status.HTTP_204_NO_CONTENT)
async def delete_profile(user : user_dependency, db : db_dependency,
                         request : DeleteProfileRequest):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = 'Invalid User')
    user_model = db.query(User).filter_by(id=user.get('id')).first()
    if verify_password(request.userPassword, user_model.hashed_password):
        db.delete(user_model)
        db.commit()
        return {'message': 'User Deleted'}
    else :
        raise HTTPException(status_code=401, detail='Invalid Password')

