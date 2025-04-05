from io import BytesIO

import aiohttp
import logging

from fastapi.encoders import jsonable_encoder

from models.api_model import User, UserCreateRequest

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


class FastAPIClient:
    def __init__(self, api_url: str):
        self.api_url = api_url
        # self.session?

    async def upload_zip(self, zip_archive: BytesIO, user) -> bool:
        return await self.__upload_zip(zip_archive, user)

    async def user_payment_info(self, user_data) -> dict:
        try:
            async with aiohttp.ClientSession() as session:
                user = User(**user_data.to_dict())

                async with session.get(
                        url=f"{self.api_url}/payment_status/{user.id}",
                ) as response:
                    response.raise_for_status()
                    data = await response.json()
                    return data
        except Exception as e:
            logging.error(f'Unexpected error: {e}. User_id: {user.id}')

    async def add_user(self, user) -> dict:
        try:
            async with aiohttp.ClientSession() as session:
                user = jsonable_encoder(
                    UserCreateRequest(**user.to_dict()))
                async with session.post(
                        url=f"{self.api_url}/add_user/", json=user
                ) as response:
                    response.raise_for_status()
                    return True
        except Exception as e:
            logging.error(f'Unexpected error: {e}. User_id: {user}')

    async def __upload_zip(self, zip_archive: BytesIO, user) -> bool:
        upload = False
        try:
            async with aiohttp.ClientSession() as session:
                value_user = User(**user.to_dict()).model_dump_json()

                data = aiohttp.FormData()
                data.add_field(
                    name='file',
                    value=zip_archive,
                    filename='archive.zip',
                    content_type='application/zip'
                )

                data.add_field(
                    name='user',
                    value=value_user,
                    content_type='application/json'
                )

                async with session.post(f"{self.api_url}/upload_zip/", data=data) as response:
                    response.raise_for_status()
                    upload = True
        except Exception as e:
            logging.error(f'Unexpected error: {e}. User_id: {user.id}')
        finally:
            zip_archive.close()
            logging.info(f"Zip_buffer closed. File uploaded: {upload}. User_id: {user.id}")
            return upload

# https://v3.fal.media/files/tiger/ibCRjc9iBXG1mihE01y76_pytorch_lora_weights.safetensors
