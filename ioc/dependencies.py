from fastapi import Depends

from application.main import database
from db.repositories import PQSLRepository
from services.user_service.user_service import UserService
from storage.client import S3ClientABC, get_s3_client


async def async_session():
    async with database.session_scope() as session:
        yield session

def psql_repository(session = Depends(async_session)) -> PQSLRepository:
    return PQSLRepository(session)

def s3_client_dependency() -> S3ClientABC:
    return get_s3_client()

def user_service(repository = Depends(psql_repository)) -> UserService:
    return UserService(repository)


