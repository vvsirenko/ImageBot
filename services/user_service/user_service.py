import uuid
from typing import Final

from starlette.responses import JSONResponse

from db.repositories import PQSLRepository


class UserService:
    def __init__(self, repository: PQSLRepository):
        self._repository: Final = repository

    async def payment_status(self,  user_id: int) -> JSONResponse:
        result = await self._repository.payment_status(user_id)
        return result

    async def add_user(
            self,
            tg_id: int,
            username: str,
            first_name: str,
            last_name: str,
            referral_link: str,
            referrer_id: uuid.UUID | None = None,
    ) -> JSONResponse:
        result = await self._repository.add_user(
            tg_id=tg_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            referral_link=referral_link,
            referrer_id=referrer_id,
        )
        return result
