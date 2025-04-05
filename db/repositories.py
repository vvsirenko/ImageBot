import uuid
from collections.abc import Callable
from datetime import datetime
from functools import wraps

from fastapi.responses import JSONResponse
from sqlalchemy import Result, Select, insert, select
from sqlalchemy.exc import IntegrityError

from app_config import get_app_config
from db.models.async_database import AsyncDataBase
from db.models.base import User
from db.servicies import Service
from rest_api.models import ErrorMessage


def exception_handler(func: Callable) -> Callable:
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            print(f"An error occurred: {e}")
            return JSONResponse(
                content=ErrorMessage(e).model_dump(),
                status_code=500,
            )
    return wrapper


class PQSLRepository:
    def __init__(self, database: "AsyncDataBase"):
        self._database = database

    @exception_handler
    async def payment_status(self, user_id: int) -> JSONResponse:
        # call to table in db to get payment_status
        prepared_answer = {"status": "success", "data": {}}
        return prepared_answer

    @exception_handler
    async def add_user(
            self,
            tg_id: int,
            username: str,
            first_name: str,
            last_name: str,
            referral_link: str,
            referrer_id: uuid.UUID | None = None,
    ):
        try:

            statement: Select = select(User).where(User.tg_id == tg_id)
            result: Result = await self._database.execute(statement)
            user = result.scalars().first()

            if not user:
                user_data = {
                    "tg_id": tg_id,
                    "username": username,
                    "first_name": first_name,
                    "last_name": last_name,
                    "referral_link": referral_link,
                    "referrer_id": referrer_id,
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow(),
                }
                statement = insert(User).values(**user_data).returning(User)
                result = await self._database.execute(statement)
                await self._database.commit()
                return result.scalars().first()

        except IntegrityError:
            await self._database.rollback()
            raise Exception("Failed to add user due to a database constraint violation.")
        except Exception as e:
            await self._database.rollback()
            raise Exception(f"Database error: {e!s}")


database: AsyncDataBase = AsyncDataBase(app_config=get_app_config())
repository: PQSLRepository = PQSLRepository(database=database)
service: Service = Service(repository)


def get_service() -> Service:
    return service
