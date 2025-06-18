from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from starlette.status import HTTP_200_OK, HTTP_401_UNAUTHORIZED
from configs.database import get_db
from exception import raise_error
from schemas.authentication import Register
from services.authentication_services import get_authentication_service
from schemas.authentication import Token

router = APIRouter(
    prefix="/api/auth",
    tags=["auth"],
)

@router.post("/login",status_code=HTTP_200_OK, response_model=Token)
async def login(
    request = Depends(OAuth2PasswordRequestForm),
    db = Depends(get_db),
    authen_service = Depends(get_authentication_service),

):
        response = authen_service.authenticate(request.username, request.password, db)
        if response is False:
            raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
        return response


@router.post("/register")
async def register(
    request: Register,
    db = Depends(get_db),
    authen_service = Depends(get_authentication_service)
):
    try:
        return authen_service.create_user(request, db)
    except Exception:
        return raise_error(100004)

