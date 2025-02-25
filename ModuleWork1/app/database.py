from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class User:
    username: str
    password_hash: bytes
    full_name: Optional[str]
    links: set

    def key(self):
        return self.username.lower()


@dataclass
class Url:
    url: str
    created_at: datetime
    short: str
    owner: str
    redirects: list[datetime]

    def key(self):
        return self.short


class Database:
    def __init__(self):
        self._users = {}
        self._urls = {}

    def find_user(self, username: str) -> Optional[User]:
        return self._users.get(username)

    def save_user(self, user: User):
        key = user.key()
        self._users[key] = user

    def save_url(self, url: Url):
        owner = self.find_user(url.owner.lower())
        assert owner is not None
        key = url.key()
        owner.links.add(key)
        url.redirects.sort()
        self._urls[key] = url

    def find_url(self, short: str) -> Optional[Url]:
        return self._urls.get(short)

    @classmethod
    def instance(cls):
        if getattr(cls, "_instance", None) is None:
            cls._instance = cls()
        return cls._instance


db = Database.instance()
