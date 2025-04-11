from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from application.main import database
from db.repositories import PQSLRepository, AbsDBRepository
from services.user_service.user_service import UserService
from storage.client import S3ClientABC, get_s3_client


async def async_session():
    async with database.get_session() as session:
        yield session


def psql_repository(
        session: AsyncSession = Depends(async_session)
) -> AbsDBRepository:
    return PQSLRepository(session)


def s3_client_dependency() -> S3ClientABC:
    return get_s3_client()


def user_service(
        repository: AbsDBRepository = Depends(psql_repository)
) -> UserService:
    return UserService(repository)


