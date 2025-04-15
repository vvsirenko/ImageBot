import abc
from typing import Any

from telegram import Update

from domain.dto import UserTgModel
from telegram_bot.domain.user import User


class UserService:
    def __init__(self, user_repo):
        self.user_repo = user_repo


class UseCase(abc.ABC):
    @abc.abstractmethod
    async def execute(self):
        ...


class UseCaseResult:
    result: Any
    error: Exception


class CreateAvatare(UseCase):

    def __init__(self, user_repo, user, files_of_bytes: list[BytesIO]):
        self.user_repo = user_repo
        self.user = user

    async def execute(self):

        # service steps
        # __upload_zip(self, zip_archive: BytesIO, user: dict)
        try:
            user = await self.user_repo.add_user(user=self.user)
            return UseCaseResult(result=user, error=None)
        except Exception as e:
            return UseCaseResult(result=None, error=e)