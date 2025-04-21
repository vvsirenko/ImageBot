import json
import logging
import aiohttp

from io import BytesIO

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


class FastAPIClient:
    def __init__(self, api_url: str):
        self.api_url = api_url
        # self.session?

    async def upload_zip(self, zip_archive: BytesIO, user: dict) -> bool:
        return await self.__upload_zip(zip_archive, user)

    async def user_payment_info(self, user: dict) -> dict:
        try:
            async with aiohttp.ClientSession() as session:
                user_id = user.get("user_id", None)
                async with session.get(
                        url=f"{self.api_url}/payment_status/{user_id}",
                ) as response:
                    response.raise_for_status()
                    data = await response.json()
                    return data
        except Exception as e:
            logging.exception(
                f"Unexpected error: {e}. User_id: {user.get('id', None)}"
            )

    async def add_user(self, user: dict) -> bool:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                        url=f"{self.api_url}/add_user/", json=user
                ) as response:
                    response.raise_for_status()
                    return True
        except Exception as e:
            logging.exception(
                f"Unexpected error: {e}. User_id: {user.get('id', None)}"
            )

    async def __upload_zip(self, zip_archive: BytesIO, user: dict) -> bool:
        upload = False
        try:
            async with aiohttp.ClientSession() as session:

                data = aiohttp.FormData()
                data.add_field(
                    name="file",
                    value=zip_archive,
                    filename="archive.zip",
                    content_type="application/zip",
                )
                user_value = json.dumps(user, ensure_ascii=False)
                data.add_field(
                    name="user",
                    value=user_value,
                    content_type="application/json"
                )

                async with session.post(f"{self.api_url}/upload_zip/", data=data) as response:
                    response.raise_for_status()
                    upload = True
        except Exception as e:
            logging.exception(f"Unexpected error: {e}. User_id: {user.get('id', None)}")
        finally:
            zip_archive.close()
            logging.info(
                f"Zip_buffer closed. File uploaded: {upload}. User_id: {user.get('id', None)}"
            )
            return upload

# https://v3.fal.media/files/tiger/ibCRjc9iBXG1mihE01y76_pytorch_lora_weights.safetensors
