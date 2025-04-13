import asyncio
from contextlib import asynccontextmanager
from typing import Any

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from app_config import AppConfig


class AsyncDataBase:
    connect_args = {"timeout": 2}  # TODO from config

    def __init__(self, app_config: AppConfig):
        self._engine: AsyncEngine = create_async_engine(
            app_config.DATABASE_URL,
            echo=True,
            connect_args=self.connect_args,
            pool_size=20,
            max_overflow=10,
        )
        self._session: async_sessionmaker[AsyncSession | Any] = async_sessionmaker(
            self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

    @asynccontextmanager
    async def get_session(self):
        """Контекстный менеджер для управления сессией и транзакциями."""
        async with self._session() as session:
            try:
                yield session
            except asyncio.exceptions.TimeoutError:
                raise Exception("Database timeout error")
            except Exception as e:
                raise e

