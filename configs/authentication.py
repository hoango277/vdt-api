import os
from typing import Annotated

from dotenv import load_dotenv
from fastapi import Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from starlette import status
from starlette.status import HTTP_403_FORBIDDEN, HTTP_401_UNAUTHORIZED
from datetime import timedelta, datetime, timezone
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from starlette.status import HTTP_201_CREATED, HTTP_404_NOT_FOUND, HTTP_200_OK, HTTP_401_UNAUTHORIZED
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError

load_dotenv()

SECRET_KEY = os.getenv("PRIVATE_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

class CustomOAuth2PasswordBearer(OAuth2PasswordBearer):
    async def __call__(self, request: Request):
        from fastapi.security.utils import get_authorization_scheme_param
        authorization = request.headers.get("Authorization")
        scheme, param = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "bearer":
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return param

# Sử dụng custom oauth2 scheme
custom_oauth2_scheme = CustomOAuth2PasswordBearer(tokenUrl="/api/auth/login")

def verify_password(plain_password, hashed_password):
    return password_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return password_context.hash(password)


def create_access_token(username: str, user_id: int, user_role:str ,expires_delta: timedelta):
    encode = {'sub' : username, 'id' : user_id, 'role' : user_role}
    expire = datetime.now(timezone.utc) + expires_delta
    encode.update({'exp' : expire})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: Annotated[str, Depends(custom_oauth2_scheme)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        user_role : str = payload.get('role')
        if username is None or user_id is None:
            raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail= 'Cannot validate user!')
        return {'username': username, 'user_id': user_id, 'user_role': user_role}
    except JWTError:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail= 'Cannot validate user!')



