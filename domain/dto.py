import uuid
from uuid import UUID
from typing import Optional
from pydantic import BaseModel, Field


class StringsInput(BaseModel):
    strings: list[str]


class User(BaseModel):
    id: int | str
    first_name: str | None
    last_name: str | None = None
    is_bot: bool = False
    is_premium: bool = False
    language_code: str | None = None
    username: str | None = None


class CreateUserDTO(BaseModel):
    tg_id: int = Field(alias="id")
    first_name: str | None = None
    last_name: str | None = None
    username: str | None = None
    referral_link: str | None = Field(
        default_factory=lambda data:
        f"https://t.me/fast_market_api_bot?start={data['tg_id']}",
    )
    referrer_id: UUID = Field(default=uuid.uuid4())

    class Config:
        json_encoders = {
            UUID: lambda v: str(v),
        }


class UserTgModel(BaseModel):
    id: Optional[int] = Field(default=None)
    first_name: Optional[str] = Field(default=None)
    last_name: Optional[str] = Field(default=None)
    username: Optional[str] = Field(default=None)
    is_premium: Optional[bool] = Field(default=None)
    language_code: Optional[str] = Field(default=None)

    def to_dict(self) -> dict:
        return self.dict(exclude_none=True)

    @classmethod
    def from_update(cls, update) -> "UserModel":
        effective_user = getattr(update, 'effective_user', None)
        if not effective_user:
            return cls()

        return cls(
            id=getattr(effective_user, 'id', None),
            first_name=getattr(effective_user, 'first_name', None),
            last_name=getattr(effective_user, 'last_name', None),
            username=getattr(effective_user, 'username', None),
            is_premium=getattr(effective_user, 'is_premium', None),
            language_code=getattr(effective_user, 'language_code', None)
        )