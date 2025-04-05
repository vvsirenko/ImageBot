from io import BytesIO

from libs.image_caption_generator.main import AsyncImageCaptionGenerator


class CaptionService:
    def __init__(self, image_caption_generator: AsyncImageCaptionGenerator):
        self._image_caption_generator = image_caption_generator

    async def generate_caption(self, file_bytes: BytesIO):
        await self._image_caption_generator.generate_caption(file_bytes)
