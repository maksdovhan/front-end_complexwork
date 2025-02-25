from datetime import datetime
from typing import Optional

from pydantic import AnyHttpUrl, BaseModel, Field


class Detailed(BaseModel):
    """Generic model which is used to document error responses"""

    detail: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str]


class CreateUserModel(BaseModel):
    """Describes an entity which is used to create a new user"""

    username: str = Field(
        min_length=3,
        max_length=20,
        pattern=r"^[a-zA-Z0-9_]+$",
        examples=["johndoe2024"],
        description="Uniq username which identifies the user, case-insensitive",
    )
    password: str = Field(min_length=8, examples=["$3cr3tP@ssw0rd"])
    full_name: Optional[str] = Field(max_length=64, examples=["John Doe"], default=None)


class UserModel(BaseModel):
    """Representation of user"""

    username: str = Field(examples=["johndoe2024", "Grady_Booch"])
    full_name: Optional[str] = Field(examples=[None, "Grady Booch"])
    links: int = Field(
        ge=0,
        examples=[0, 100, 200],
        description="Count of the short URLs, user created",
    )


class URLModel(BaseModel):
    url: AnyHttpUrl = Field(
        examples=["https://example.com"], description="Must be a valid http/https URL"
    )
    short: str = Field(
        examples=["deadbeef"],
        description="Short identifier of the URL, generated automatically. Append that to root path to get redirected",
    )
    owner: str = Field(examples=["johndoe2024"])
    redirects: int = Field(
        ge=0, examples=[0], description="Count of times this URL was used"
    )
    created_at: datetime


class CreateURLModel(BaseModel):
    url: AnyHttpUrl


class PageParams(BaseModel):
    page: int = Field(gt=0, default=1, examples=[1, 2, 3])
