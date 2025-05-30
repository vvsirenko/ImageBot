import uuid
from abc import ABC, abstractmethod
from collections.abc import Callable
from datetime import datetime
from functools import wraps
from typing import Any

from fastapi.responses import JSONResponse
from sqlalchemy import Result, insert, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.base import User, Payment
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


class AbsDBRepository(ABC):

    @abstractmethod
    async def payment_status(self, user_id: int) -> JSONResponse:
        pass

    @abstractmethod
    async def add_user(
        self,
        tg_id: int,
        username: str,
        first_name: str,
        last_name: str,
        referral_link: str,
        referrer_id: uuid.UUID | None = None,
    ) -> Any:
        pass


class PQSLRepository(AbsDBRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    @exception_handler
    async def payment_status(self, user_id: int | None) -> JSONResponse:
        try:
            statement = select(Payment).where(User.tg_id == user_id)
            result = await self._session.execute(statement)
            records = result.scalars().all()
            if not records:
                return None
            if len(records) > 1:
                raise Exception(f"Found multiple payment with tg_id={user_id}")
            return records[0]
        except IntegrityError as e:
            raise Exception(
                "Failed to fetch_payment due to a database constraint violation.") from e
        except Exception as e:
            raise Exception(f"Database error: {e!s}") from e

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
            statement = select(User).where(User.tg_id == tg_id)
            result: Result = await self._session.execute(statement)
            if result.scalars().one_or_none():
                return None

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
            result = await self._session.execute(statement)
            await self._session.commit()
            return result.scalars().one_or_none()
        except IntegrityError:
            raise Exception("Failed to add user due to a database constraint violation.")
        except Exception as e:
            raise Exception(f"Database error: {e!s}")

    @exception_handler
    async def fetch_profile(self, user_id: int):
        try:
            statement = select(User).where(User.tg_id == user_id)
            result = await self._session.execute(statement)
            records = result.scalars().all()
            if not records:
                return None
            if len(records) > 1:
                raise Exception(f"Found multiple users with tg_id={user_id}")
            return records[0].to_dict()
        except IntegrityError as e:
            raise Exception(
                "Failed to fetch_profile due to a database constraint violation.") from e
        except Exception as e:
            raise Exception(f"Database error: {e!s}") from e