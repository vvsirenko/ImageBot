import abc

import aiohttp
import logging

from fal_client import result

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


class AbcUserRepository(abc.ABC):
    @abc.abstractmethod
    async def add_user(self, user: dict) -> bool:
        ...

    @abc.abstractmethod
    async def fetch_profile(self, user_id: str) -> bool:
        ...


class UserRepository(AbcUserRepository):
    def __init__(self, base_url: str):
        self.base_url = base_url

    async def add_user(self, user: dict) -> bool:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                        url=f"{self.base_url}/add_user/", json=user
                ) as response:
                    response.raise_for_status()
                    return True
        except Exception as e:
            logging.exception(
                f"Unexpected error: {e}. User_id: {user.get('id', None)}"
            )
            return None

    async def fetch_profile(self, user_id: str) -> bool:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                        url=f"{self.base_url}/users/{user_id}"
                ) as response:
                    response.raise_for_status()
                    result = await response.json()
                    if "fetch_profile" in result and result["fetch_profile"] == "true":
                        return True
                    else:
                        return False
        except Exception as e:
            logging.exception(
                f"Unexpected error: {e}. User_id: {user_id}"
            )
            return None



