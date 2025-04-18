from pydantic import BaseModel, Field, PlainValidator
from typing import Optional, Annotated

from telegram_bot.user_repository import AbcUserRepository


UserId = Annotated[int, PlainValidator(lambda v: v if isinstance(v, int) and v > 0 else ValueError("UserId must be a positive integer"))]

FirstName = Annotated[str, PlainValidator(lambda v: v.strip() if isinstance(v, str) and v.strip() else ValueError("FirstName must be a non-empty string"))]

LastName = Annotated[str, PlainValidator(lambda v: v.strip() if isinstance(v, str) else ValueError("LastName must be a string"))]

Username = Annotated[str, PlainValidator(lambda v: v if isinstance(v, str) else ValueError("Username must be a string"))]

IsPremium = Annotated[bool, PlainValidator(lambda v: bool(v) if isinstance(v, bool) else ValueError("IsPremium must be a boolean"))]

IsBot = Annotated[bool, PlainValidator(lambda v: bool(v) if isinstance(v, bool) else ValueError("IsBot must be a boolean"))]

LanguageCode = Annotated[str, PlainValidator(lambda v: v.lower() if isinstance(v, str) and len(v) == 2 else ValueError("LanguageCode must be 2-letter string"))]


class TelegramUser(BaseModel):

    id: Optional[UserId] = Field(default=None)
    first_name: Optional[FirstName] = Field(default=None)
    last_name: Optional[LastName] = Field(default=None)
    username: Optional[Username] = Field(default=None)
    is_premium: Optional[IsPremium] = Field(default=False)
    language_code: Optional[LanguageCode] = Field(default=None)
    is_bot: Optional[IsBot] = Field(default=False)

    def to_dict(self) -> dict:
        return self.dict(exclude_none=True)

    async def fetch_profile(self, repo: AbcUserRepository) -> dict:
        # TODO: check if user is in db, if not, add it, decide how to handle this case
        data = await repo.fetch_profile(self.id)
        if not data:
            await repo.add_user(self.to_dict())

