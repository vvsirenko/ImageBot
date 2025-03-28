import asyncio
from typing import Any

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, \
    async_sessionmaker, AsyncSession
from sqlalchemy import select, Select, Result

from app_config import AppConfig


class AsyncDataBase:
    connect_args = {"timeout": 2}  # TODO from config

    def __init__(self, app_config: AppConfig):
        self._engine: AsyncEngine = create_async_engine(
            app_config.DATABASE_URL, echo=True, connect_args=self.connect_args
        )
        self._session: async_sessionmaker[
            AsyncSession | Any] = async_sessionmaker(
            self._engine, class_=AsyncSession, expire_on_commit=False
        )

    def get_session(self) -> AsyncSession:
        return self._session()

    async def execute(self, statement: "Select") -> "Result":
        try:
            async with self.get_session() as asession:
                result: "Result" = await asession.execute(statement)
        except asyncio.exceptions.TimeoutError as e:
            raise Exception("Database timeout error") from e
        except Exception as e:
            raise Exception(e)
        return result

    async def commit(self):
        try:
            async with self.get_session() as asession:
                await asession.commit()
        except asyncio.exceptions.TimeoutError as e:
            raise Exception("Database timeout error") from e
        except Exception as e:
            raise Exception(e)

    async def rollback(self):
        try:
            async with self.get_session() as asession:
                await asession.rollback()
        except asyncio.exceptions.TimeoutError as e:
            raise Exception("Database timeout error") from e
        except Exception as e:
            raise Exception(e)