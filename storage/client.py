import logging
import os
import uuid
from io import BufferedReader

import aiohttp
from abc import ABC, abstractmethod

from typing import Any
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


class S3ClientABC(ABC):
    @abstractmethod
    async def upload_file(
            self, file_path_image: str,
            cloud_url: str, user: Any
    ) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def upload_zip(
            self, files: dict,
            cloud_url: str,
            user
    ) -> bool:
        raise NotImplementedError


class S3Client(S3ClientABC):
    def __init__(self, cloud_token: str):
        self.cloud_token = cloud_token
        self.upload_header = {'Authorization': 'Bearer ' + cloud_token}

    async def upload_file(
            self, file_path_image: str,
            cloud_url: str, user: str
    ) -> bool:
        return await self.__upload_file(file_path_image, cloud_url, user)

    async def __upload_file(
            self, file_path_image: str,
            cloud_url: str, user
    ) -> bool:
        is_send = False
        try:
            async with aiohttp.ClientSession(headers=self.upload_header) as session:
                # user_id = user.get('id', '')
                user_id = user.id

                image_bytes = await self.get_file_from_tg(file_path_image)

                params = {'path': f'/{user_id}/training/'}
                data = {f'{uuid.uuid4()}': image_bytes}
                async with session.post(cloud_url, data=data, params=params) as response:
                    response.raise_for_status()
                    if response.status == 204:
                        is_send = True
        except aiohttp.ClientError as e:
            logging.error(f'Client error: {e} user_id: {user_id}')
        except aiohttp.http_exceptions.HttpProcessingError as e:
            logging.error(f'HTTP processing error: {e}')
        except Exception as e:
            logging.error(f'Unexpected error: {e}')
        finally:
            return is_send

    async def upload_zip(self, files: BufferedReader | Any,
                         cloud_url: str, user) -> dict:
        try:
            async with aiohttp.ClientSession(headers=self.upload_header) as session:
                data = aiohttp.FormData()

                with open(files.name, "rb") as file:
                    buffered_file = file.read()
                data.add_field(
                    name="file",
                    value=buffered_file,
                    filename=f"archive_{user.id}",
                    content_type="application/zip"
                )
                params = {'path': f'/{user.id}/training/'}
                async with session.post(cloud_url, data=data, params=params) as response:
                    return {
                        "status": response.status,
                        "error": None
                    }
        except aiohttp.ClientError as e:
            logging.error(f'Client error: {e} user_id: {user.id}')
            return {
                "status": 400,
                "error": f'ClientError: {str(e)}'
            }
        except aiohttp.ClientTimeout as e:
            logging.error(f'TimeoutError error: {e} user_id: {user.id}')
            return {
                "status": 400,
                "error": 'TimeoutError: Request timed out'
            }
        except aiohttp.http_exceptions.HttpProcessingError as e:
            logging.error(f'HTTP processing error: {e}')
            return {
                "status": 400,
                "error": 'HTTP processing error'
            }
        except Exception as e:
            logging.error(f'Unexpected error: {e}')
            return {
                "status": 400,
                "error": 'HUnexpected error'
            }

    async def get_file_from_tg(self, file_url: str):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(file_url) as resp:
                    file_bytes = await resp.read()
                    return file_bytes
        except aiohttp.ClientError as e:
            logging.error(f'Client error: {e} file_url: {file_url}')
        except aiohttp.http_exceptions.HttpProcessingError as e:
            logging.error(f'HTTP processing error: {e}')
        except Exception as e:
            logging.error(f'Unexpected error: {e}')


def get_s3_client():
    load_dotenv() #todo: move to settings
    return S3Client(os.environ.get('TIMEWEB_CLOUD_TOKEN', ''))