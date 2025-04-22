import abc

import aiohttp
import logging

from fal_client import result

from domain.models import BaseResponse

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


class AbcUserRepository(abc.ABC):
    @abc.abstractmethod
    async def add_user(self, user: dict) -> 'BaseResponse':
        ...

    @abc.abstractmethod
    async def fetch_profile(self, user_id: str) -> 'BaseResponse':
        ...

    @abc.abstractmethod
    async def fetch_payment_info(self, user_id: str) -> 'BaseResponse':
        ...

    @abc.abstractmethod
    async def get_by_id(self, user_id: str) -> 'BaseResponse':
        ...

    @abc.abstractmethod
    async def save(self, user_id: str) -> 'BaseResponse':
        ...


class UserRepository(AbcUserRepository):
    def __init__(self, base_url: str):
        self.base_url = base_url

    async def add_user(self, user: dict) -> 'BaseResponse':
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                        url=f"{self.base_url}/add_user/", json=user
                ) as response:
                    response.raise_for_status()
                    return BaseResponse(**await response.json())
        except Exception as e:
            logging.exception(
                f"Unexpected error: {e}. User_id: {user.get('id', None)}"
            )
            return BaseResponse.fail(
                error=f"Unexpected error: {e}",
                message=f"User_id: {user.get('id', None)}"
            )

    async def fetch_profile(self, user_id: str) -> 'BaseResponse':
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                        url=f"{self.base_url}/users/{user_id}"
                ) as response:
                    response.raise_for_status()
                    return BaseResponse(**await response.json())
        except Exception as e:
            logging.exception(
                f"Unexpected error: {e}. User_id: {user_id}"
            )
            return BaseResponse.fail(
                error=f"Unexpected error: {e}", message=f"User_id: {user_id}"
            )

    async def fetch_payment_info(self, user_id: str) -> 'BaseResponse':
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                        url=f"{self.base_url}/payment_info/{user_id}"
                ) as response:
                    response.raise_for_status()
                    return BaseResponse(**await response.json())
        except Exception as e:
            logging.exception(
                f"Unexpected error: {e}. User_id: {user_id}"
            )
            return BaseResponse.fail(
                error=f"Unexpected error: {e}", message=f"User_id: {user_id}"
            )


