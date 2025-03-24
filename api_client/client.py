import asyncio
from io import BytesIO

import aiohttp
import logging
import zipfile

from description_image.client import ImageDescriptor
from models.api_model import User

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


class FastAPIClient:
    def __init__(self, api_url: str):
        self.api_url = api_url
        self.descriptor = ImageDescriptor()

    @classmethod
    async def create_zip_from_files(cls, files_of_bytes: list[BytesIO]):
        zip_buffer = BytesIO()

        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for idx, file_bytes in enumerate(files_of_bytes):
                if file_bytes:
                    zip_file.writestr(
                        f'image_{idx}.png',
                        file_bytes.getvalue()
                    )
        zip_buffer.seek(0)
        return zip_buffer

    async def __create_zip_from_images(self, files_of_byte: BytesIO, user, idx: int, zip_file):
        file_name = f"{user.id}-image-{idx}.txt"
        file = await self.descriptor.get_caption_single_image(
            files_of_byte.getvalue())

        zip_file.writestr(
            file_name,
            file
        )

        image_name = f"{user.id}-image-{idx}.png"
        zip_file.writestr(
            image_name,
            files_of_byte.getvalue()
        )

    async def create_zip_from_images(self, files_of_bytes: list[BytesIO], user: User):
        zip_buffer = BytesIO()

        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            tasks = [
                asyncio.create_task(self.__create_zip_from_images(file_bytes, user, idx, zip_file))
                for idx, file_bytes in enumerate(files_of_bytes)
            ]
            await asyncio.gather(*tasks)

        zip_buffer.seek(0)
        return zip_buffer

    async def upload_zip(self, files_of_bytes: list[BytesIO], user) -> bool:
        return await self.__upload_zip(files_of_bytes, user)

    async def __upload_zip(self, files_of_bytes: list[BytesIO], user) -> bool:
        upload = False
        try:
            async with aiohttp.ClientSession() as session:
                value_user = User(**user.to_dict()).model_dump_json()
                # zip_buffer = await self.create_zip_from_files(files_of_bytes)

                zip_buffer = await self.create_zip_from_images(files_of_bytes, user)

                data = aiohttp.FormData()
                data.add_field(
                    name='file',
                    value=zip_buffer,
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
            zip_buffer.close()
            logging.info(f"Zip_buffer closed. File uploaded: {upload}. User_id: {user.id}")
            return upload


# https://v3.fal.media/files/tiger/ibCRjc9iBXG1mihE01y76_pytorch_lora_weights.safetensors






