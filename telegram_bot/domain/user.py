from dependency import inject

from domain.dto import UserTgModel

from pydantic import BaseModel, Field, validator
from typing import Optional
from pydantic.errors import StrRegexError


class UserId(int):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not isinstance(v, int):
            raise TypeError("UserId must be an integer")
        if v <= 0:
            raise ValueError("UserId must be a positive integer")
        return cls(v)


class FirstName(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not isinstance(v, str):
            raise TypeError("FirstName must be a string")
        if len(v.strip()) == 0:
            raise ValueError("FirstName cannot be empty")
        return cls(v.strip())


class LastName(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if v is None:
            return None
        if not isinstance(v, str):
            raise TypeError("LastName must be a string")
        return cls(v.strip())


class Username(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not isinstance(v, str):
            raise TypeError("Username must be a string")
        if not v.startswith('@'):
            raise ValueError("Username must start with '@'")
        return cls(v)


class IsPremium(bool):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        return bool(v)


class LanguageCode(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not isinstance(v, str):
            raise TypeError("LanguageCode must be a string")
        if len(v) != 2:
            raise ValueError("LanguageCode must be a 2-letter code")
        return cls(v.lower())


class TelegramUser(BaseModel):

    id: Optional[UserId] = Field(default=None)
    first_name: Optional[FirstName] = Field(default=None)
    last_name: Optional[LastName] = Field(default=None)
    username: Optional[Username] = Field(default=None)
    is_premium: Optional[IsPremium] = Field(default=None)
    language_code: Optional[LanguageCode] = Field(default=None)

    def to_dict(self) -> dict:
        return self.dict(exclude_none=True)

    async def fetch_profile(self, repo):
        data = await repo.fetch_profile(self.user_id)
        if not data:
            await self.repo.add_user(self.user_data)

