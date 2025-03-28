import uuid
from uuid import UUID

from pydantic import BaseModel, Field


class StringsInput(BaseModel):
    strings: list[str]


class User(BaseModel):
    id: int | str
    first_name: str | None
    last_name: str | None
    is_bot: bool = False
    is_premium: bool = False
    language_code: str | None = None
    username: str | None = None


class UserCreateRequest(BaseModel):
    tg_id: int = Field(alias='id')
    first_name: str | None = None
    last_name: str | None = None
    username: str | None = None
    referral_link: str | None = Field(
        default_factory=lambda data:
        f"https://t.me/fast_market_api_bot?start={data['tg_id']}"
    )
    referrer_id: UUID = Field(default=uuid.uuid4())

    class Config:
        json_encoders = {
            UUID: lambda v: str(v),
        }
