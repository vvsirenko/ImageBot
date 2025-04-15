import aiohttp
import requests
import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


class UserRepository:
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

    async def fetch_profile(self, user_id: str) -> bool:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                        url=f"{self.base_url}/users/{user_id}"
                ) as response:
                    response.raise_for_status()
                    return True
        except Exception as e:
            logging.exception(
                f"Unexpected error: {e}. User_id: {user_id}"
            )

