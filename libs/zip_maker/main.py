import asyncio
from io import BytesIO
import zipfile
from models.api_model import User
from concurrent.futures import ProcessPoolExecutor


class ZipCreator:
    def __init__(
            self,
            executor: ProcessPoolExecutor
    ):
        self._executor = executor

    async def create_zip_from_images(
            self,
            *,
            files_of_bytes: list[BytesIO],
            captions: list[str],
            user: User
    ) -> BytesIO:
        loop = asyncio.get_running_loop()
        zip_bytes = await loop.run_in_executor(
            self._executor,
            self._create_zip,
            files_of_bytes,
            captions,
            user
        )

        return zip_bytes

    @staticmethod
    def _create_zip(files_of_bytes, captions, user):
        zip_buffer = BytesIO()

        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for idx, (file_bytes, caption) in enumerate(zip(files_of_bytes, captions)):
                caption_name = f"{user.id}-image-{idx}.txt"
                zip_file.writestr(caption_name, caption)

                image_name = f"{user.id}-image-{idx}.png"
                zip_file.writestr(image_name, file_bytes.getvalue())

        zip_buffer.seek(0)
        return zip_buffer

