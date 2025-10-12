from datetime import timedelta, datetime, timezone
from typing import Annotated
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from pydantic import BaseModel, EmailStr, Field
from starlette import status
from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRES_MINUTES
from dependencies import db_dependency
from security import hash_password, verify_password
from models import User

router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

class CreateUserRequest(BaseModel):
    email : EmailStr
    password : str = Field(min_length=8, max_length=20)

class Token(BaseModel):
    access_token:str
    token_type:str

def authenticate_user(username:str, password:str, db):
    user = db.query(User).filter_by(email=username).first()
    if user and verify_password(password, user.hashed_password):
        return user
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid Credentials')

def create_access_token(email:str, user_id:int, created_at: datetime):
    encode = {
        'email':email,
        'id':user_id,
        'created_at':created_at.isoformat()
    }
    expires = datetime.now(timezone.utc) + ACCESS_TOKEN_EXPIRES_MINUTES
    encode.update({'exp':expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

@router.post('/register', status_code=status.HTTP_201_CREATED)
async def create_user(db:db_dependency,
                      create_user_request : CreateUserRequest):
    existing_user = db.query(User).filter_by(email=create_user_request.email).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Email already registered')
    create_user_model = User(
        email = create_user_request.email,
        hashed_password = hash_password(create_user_request.password)
    )
    db.add(create_user_model)
    db.commit()
    db.refresh(create_user_model)
    return {
        'message':'User created successfully',
        'id':create_user_model.id,
        'email':create_user_model.email
    }

@router.post('/token', response_model=Token)
async def login_for_access_token(db:db_dependency,
                                 form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = authenticate_user(form_data.username, form_data.password, db)
    token = create_access_token(user.email, user.id, user.created_at)
    return {'access_token' : token, 'token_type' : 'bearer'}