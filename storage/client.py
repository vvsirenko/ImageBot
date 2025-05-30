import logging
import os
import uuid
from abc import ABC, abstractmethod
from io import BufferedReader
from typing import Any

import aiohttp
from dotenv import load_dotenv
from fastapi import HTTPException, status

from rest_api.models import ResponseModel

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


class S3ClientABC(ABC):
    service_name = "s3"

    @abstractmethod
    async def upload_file(
            self, file_path_image: str,
            cloud_url: str, user: Any,
    ) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def upload_zip(
            self, files: dict,
            cloud_url: str,
            user,
    ) -> bool:
        raise NotImplementedError


class S3Client(S3ClientABC):
    service_name = "timecloude"

    def __init__(self, cloud_token: str):
        self.cloud_token = cloud_token
        self.upload_header = {"Authorization": "Bearer " + cloud_token}

    async def upload_file(
            self, file_path_image: str,
            cloud_url: str, user: str,
    ) -> bool:
        return await self.__upload_file(file_path_image, cloud_url, user)

    async def __upload_file(
            self, file_path_image: str,
            cloud_url: str, user,
    ) -> bool:
        is_send = False
        try:
            async with aiohttp.ClientSession(headers=self.upload_header) as session:
                user_id = user.id
                image_bytes = await self.get_file_from_tg(file_path_image)
                params = {"path": f"/{user_id}/training/"}
                data = {f"{uuid.uuid4()}": image_bytes}
                async with session.post(cloud_url, data=data, params=params) as response:
                    response.raise_for_status()
                    if response.status == 204:
                        is_send = True
        except aiohttp.ClientError as e:
            logging.exception(f'Client error: {e} user_id: {user_id if user.id else "unknown"}')
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=ResponseModel(
                    status="error",
                    error=str(e),
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    message="Error connecting to S3",
                ).dict(),
            )
        except aiohttp.http_exceptions.HttpProcessingError as e:
            logging.exception(f"HTTP processing error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=ResponseModel(
                    status="error",
                    error=str(e),
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    message="HTTP processing error during S3 upload",
                ).dict(),
            )
        except Exception as e:
            logging.exception(f"Unexpected error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=ResponseModel(
                    status="error", error=str(e),
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    message="Unexpected error during S3 upload",
                ).dict(),
            )
        finally:
            return is_send

    async def upload_zip(self, files: BufferedReader | Any, cloud_url: str, user) -> dict:
        response = None
        try:
            async with (aiohttp.ClientSession(headers=self.upload_header) as session):
                with open(files.name, "rb") as file:
                    buffered_file = file.read()
                data = aiohttp.FormData()
                data.add_field(
                    name="file",
                    value=buffered_file,
                    filename=f"archive_{user.id}",
                    content_type="application/zip",
                )
                params = {"path": f"/{user.id}/training/"}
                async with session.post(cloud_url, data=data, params=params) as response:
                    response.raise_for_status()
                    if response.status == 204:
                        return {"success": True}
        except FileNotFoundError as exp:
            logging.exception(
                    f"File not found: {files.name} "
                    f"user_id: {user.id if user.id else 'unknown'}",
                )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ResponseModel(
                    status="error",
                    error=str(exp),
                    status_code=status.HTTP_404_NOT_FOUND,
                    message=f"FileNotFoundError: File '{files.name}' not found.",
                ).model_dump(),
            )
        except Exception as e:
            logging.exception(f"Unexpected error s3: {e}")
            if not response:
                status_code = status.HTTP_400_BAD_REQUEST
            else:
                status_code = response.status
            raise HTTPException(
                status_code=status_code,
                detail=ResponseModel(
                    status="error",
                    error=str(e),
                    status_code=status_code,
                    message="",
                ).model_dump(),
            )

    async def get_file_from_tg(self, file_url: str):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(file_url) as resp:
                    file_bytes = await resp.read()
                    return file_bytes
        except aiohttp.ClientError as e:
            logging.exception(f"Client error: {e} file_url: {file_url}")
        except aiohttp.http_exceptions.HttpProcessingError as e:
            logging.exception(f"HTTP processing error: {e}")
        except Exception as e:
            logging.exception(f"Unexpected error: {e}")


def get_s3_client():
    load_dotenv() #TODO: move to settings
    return S3Client(os.environ.get("TIMEWEB_CLOUD_TOKEN", ""))
