from datetime import datetime
import math
from typing import Annotated, NamedTuple
from fastapi import APIRouter, Body, Depends, HTTPException, Query, Response
from fastapi import status
from fastapi.security import OAuth2PasswordRequestForm

from .dependencies import get_auth_user
from .models import (
    CreateURLModel,
    CreateUserModel,
    Detailed,
    PageParams,
    Token,
    URLModel,
    UserModel,
)
from .logic import (
    authenticate_user,
    create_access_token,
    create_url,
    find_url,
    get_url_redirects,
    get_user_urls,
    is_username_available,
    create_user,
)

api = APIRouter()


class _Link(NamedTuple):
    url: str
    rel: str


def _links(links: list[_Link]) -> str:
    return ",".join([f'<{link.url}>; rel="{link.rel}"' for link in links])


@api.post(
    "/register",
    tags=["users"],
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_409_CONFLICT: {
            "description": "Username already taken",
            "model": Detailed,
        },
    },
)
async def register(
    input: Annotated[CreateUserModel, Body()],
    response: Response,
) -> UserModel:
    """Endpoint for registering new users

    While most of applications require two password fields to ensure user never
    mistypes their password, we use only one such field for simplicity. If you
    want to have password and verify password fields in your app, consider
    implementing them on front-end.
    """
    if not is_username_available(input.username):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Username already taken"
        )
    user = create_user(input)
    response.headers["Link"] = _links(
        [
            _Link("/login", "login"),
        ]
    )
    return user


@api.post(
    "/login",
    tags=["users"],
)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], response: Response
) -> Token:
    """Endpoint for logging in

    While rest of project endpoints work with json data, this one is
    implemented according to OAuth2 standard and accepts form-urlencoded.
    Consider it when implementing a client.
    """
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(user)
    response.headers["Link"] = _links([_Link("/api/users/me", "self")])
    return access_token


@api.get(
    "/me",
    tags=["users"],
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "This error is thrown when user is not authorized",
            "model": Detailed,
        },
    },
)
async def me(
    auth_user: Annotated[UserModel, Depends(get_auth_user)],
    response: Response,
) -> UserModel:
    """Returns currenlty authenticated user"""
    response.headers["Link"] = _links(
        [
            _Link("/api/me/links", "urls"),
        ]
    )
    return auth_user


@api.get(
    "/me/urls",
    tags=["urls"],
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "This error is thrown when user is not authorized",
            "model": Detailed,
        },
    },
)
async def list_my_urls(
    auth_user: Annotated[UserModel, Depends(get_auth_user)],
    query: Annotated[PageParams, Query()],
    response: Response,
) -> list[URLModel]:
    """Lists URLs, which were created by currenlty authenticated users.

    Result is paginated, page size is 10 items per page.
    """
    urls = get_user_urls(auth_user, query.page)
    header_links = [
        _Link("/api/me/links?page=1", "first"),
        _Link(f"/api/me/links?page={max(1, math.ceil(auth_user.links / 10))}", "last"),
    ]
    if query.page > 1:
        header_links.append(_Link(f"/api/me/links?page={query.page - 1}", "prev"))
    if query.page < math.ceil(auth_user.links / 10):
        header_links.append(_Link(f"/api/me/links?page={query.page + 1}", "next"))
    response.headers["Link"] = _links(header_links)
    return urls


@api.get(
    "/me/links/{short}/redirects",
    tags=["urls"],
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "This error is thrown when user is not authorized",
            "model": Detailed,
        },
        status.HTTP_404_NOT_FOUND: {
            "description": (
                "This error is thrown when user tries to access non-existing URL "
                "or the URL which was not created by them"
            ),
            "model": Detailed,
        },
    },
)
async def get_link_redirects(
    auth_user: Annotated[UserModel, Depends(get_auth_user)],
    short: str,
) -> list[datetime]:
    """Returns list of timestamps when URL with given {short} was clicked.
    These timestamps are ordered in the ascending order. User is allowed to
    access only info on the links they created.

    Result is not paginated, you will get all the timestamps at once.
    """
    url = find_url(short=short)
    if url is None or url.owner.lower() != auth_user.username.lower():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    redirects = get_url_redirects(url)
    return redirects


@api.post(
    "/me/urls",
    tags=["urls"],
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "This error is thrown when user is not authorized",
            "model": Detailed,
        },
    },
)
async def shorten_url(
    auth_user: Annotated[UserModel, Depends(get_auth_user)],
    input: Annotated[CreateURLModel, Body()],
) -> URLModel:
    """Creates a new shortened URL. This is not idempotent action, meaning user
    may shorten the same URL multiple times getting the different output each
    time.
    """
    return create_url(input, auth_user)
