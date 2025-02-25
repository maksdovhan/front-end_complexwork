from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from .models import UserModel
from .logic import find_user, parse_token_data


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")


async def get_auth_user(token: Annotated[str, Depends(oauth2_scheme)]) -> UserModel:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token_data = parse_token_data(token)
    if token_data.username is not None:
        user = find_user(token_data.username)
        if user is not None:
            return user
    raise credentials_exception
