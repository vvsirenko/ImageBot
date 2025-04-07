from io import BytesIO

from libs.zip_maker.main import ZipCreator
from models.api_model import User


class ZipService:

    def __init__(self, zip_creator):
        self._zip_creator: ZipCreator = zip_creator

    async def create_zip(self, files_of_bytes: list[BytesIO], captions: list[str], user: User):
        return await self._zip_creator.create_zip_from_images(
            files_of_bytes=files_of_bytes,
            captions=captions,
            user=user,
        )
