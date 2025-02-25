from datetime import datetime, timedelta, timezone
from typing import Any, Optional
import jwt
from passlib.hash import argon2
from passlib.pwd import genword
from pydantic import AnyHttpUrl

from .models import (
    CreateURLModel,
    CreateUserModel,
    Token,
    TokenData,
    URLModel,
    UserModel,
)
from .database import Url, User, db


# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "685f35dc485fa523da799afebc6466875aa347813850fcccdf2a8892eb12d132"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
URL_LENGTH = 8


def verify_password(username: str, password: str) -> bool:
    user = db.find_user(username.lower())
    return user is not None and argon2.verify(password, user.password_hash)


def hash_password(password: str) -> bytes:
    return argon2.hash(password)


def find_user(username: str) -> Optional[UserModel]:
    user = db.find_user(username.lower())
    if user is not None:
        return UserModel(
            username=user.username,
            full_name=user.full_name,
            links=len(user.links),
        )
    return None


def authenticate_user(username: str, password: str) -> Optional[UserModel]:
    if verify_password(username, password):
        return find_user(username)
    return None


def create_access_token(user: UserModel) -> Token:
    to_encode: dict[str, Any] = {"sub": user.username}
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return Token(access_token=encoded_jwt, token_type="bearer")


def parse_token_data(token: str) -> TokenData:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.InvalidTokenError:
        payload = {}
    username = payload.get("sub")
    token_data = TokenData(username=username)
    return token_data


def is_username_available(username: str) -> bool:
    return db.find_user(username.lower()) is None


def create_user(input: CreateUserModel) -> UserModel:
    user = User(
        username=input.username.lower(),
        password_hash=hash_password(input.password),
        full_name=input.full_name,
        links=set(),
    )
    db.save_user(user)
    return UserModel(
        username=user.username, full_name=user.full_name, links=len(user.links)
    )


def create_url(input: CreateURLModel, owner: UserModel) -> URLModel:
    url = Url(
        url=input.url.unicode_string(),
        created_at=datetime.now(),
        short=get_random_short(len_=URL_LENGTH),
        owner=owner.username,
        redirects=[],
    )
    db.save_url(url)
    return URLModel(
        url=AnyHttpUrl(url.url),
        short=url.short,
        owner=url.owner,
        redirects=len(url.redirects),
        created_at=url.created_at,
    )


def find_url(short: str) -> Optional[URLModel]:
    url_ = db.find_url(short)
    if url_ is None:
        return None
    return URLModel(
        url=AnyHttpUrl(url_.url),
        short=url_.short,
        owner=url_.owner,
        redirects=len(url_.redirects),
        created_at=url_.created_at,
    )


def count_redirect(url: URLModel):
    url_ = db.find_url(url.short)
    assert url_ is not None
    url_.redirects.append(datetime.now())
    db.save_url(url_)


def get_random_short(len_: int) -> str:
    assert len_ >= 3
    exists = True
    short = ""
    while exists:
        short = genword(length=len_, charset="ascii_62")
        exists = db.find_url(short) is not None
    return short


def get_user_urls(owner: UserModel, page: int) -> list[URLModel]:
    user = db.find_user(owner.username.lower())
    assert user is not None
    link_shorts = user.links
    links = [find_url(short) for short in link_shorts]
    links = [link for link in links if link is not None]
    links.sort(key=lambda link: link.created_at, reverse=True)
    return links[(page - 1) * 10 : page * 10]


def get_url_redirects(url: URLModel) -> list[datetime]:
    url_ = db.find_url(url.short)
    assert url_ is not None
    return [r for r in url_.redirects]
