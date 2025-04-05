import os
from functools import lru_cache

from dotenv import load_dotenv
from pydantic.v1 import BaseSettings

load_dotenv()


class AppConfig(BaseSettings):
    DATABASE_URL: str = \
        (f"postgresql+asyncpg://{os.environ.get('DB_LOGIN')}:"
         f"{os.environ.get('DB_PASSWORD')}@{os.environ.get('DB_HOST')}/"
         f"{os.environ.get('DB_NAME')}")


@lru_cache
def get_app_config():
    return AppConfig()
