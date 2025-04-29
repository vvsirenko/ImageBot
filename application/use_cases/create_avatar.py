import abc
from io import BytesIO
from typing import Any


class UseCase(abc.ABC):
    @abc.abstractmethod
    async def execute(self, *args, **kwargs):
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