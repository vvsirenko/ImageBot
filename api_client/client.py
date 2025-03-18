from io import BytesIO

import aiohttp
import logging
import zipfile

from models.api_model import User

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


class FastAPIClient:
    def __init__(self, api_url: str):
        self.api_url = api_url

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

    async def upload_zip(self, files_of_bytes: list[BytesIO], user):
        return await self.__upload_zip(files_of_bytes, user)

    async def __upload_zip(self, files_of_bytes: list[BytesIO], user):
        try:
            async with aiohttp.ClientSession() as session:
                zip_buffer = await self.create_zip_from_files(files_of_bytes)

                data = aiohttp.FormData()
                data.add_field(
                    name='file',
                    value=zip_buffer,
                    filename='archive.zip',
                    content_type='application/zip'
                )

                value_user = User(**user.to_dict()).model_dump_json()
                data.add_field(
                    name='user',
                    value=value_user,
                    content_type='application/json'
                )

                async with session.post(f"{self.api_url}/upload_zip/", data=data) as response:
                    response.raise_for_status()
                    return True
        except Exception as e:
            return
        finally:
            zip_buffer.close()






