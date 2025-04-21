import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from alembic import context

from db.models.base import Base

config = context.config
sqlalchemy_url = config.get_main_option("sqlalchemy.url")
connectable = create_async_engine(sqlalchemy_url, echo=True)
target_metadata = Base.metadata

async def run_migrations_online():
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

def do_run_migrations(connection):
    context.configure(
        connection=connection,
        target_metadata=target_metadata
    )
    with context.begin_transaction():
        context.run_migrations()

# Запуск миграций
if context.is_offline_mode():
    raise Exception("Offline mode is not supported with asyncpg")
else:
    asyncio.run(run_migrations_online())
