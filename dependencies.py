from typing import Annotated
from datetime import datetime
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from starlette import status

from database import SessionLocal
from config import SECRET_KEY, ALGORITHM


async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')
def get_current_user(token : Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, ALGORITHM)
        user_name : str = payload.get('email')
        user_id : int = payload.get('id')
        usercreated_at : datetime = datetime.fromisoformat(payload.get('created_at'))
        user_role : str = payload.get('role')

        if user_id is None or user_name is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid User')
        return {'email':user_name, 'id':user_id, 'created_at':usercreated_at, 'role': user_role}

    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid User')


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


