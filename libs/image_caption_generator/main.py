import asyncio
from concurrent.futures import ProcessPoolExecutor
from io import BytesIO

from libs.image_caption_generator.image_caption_generator import ImageCaptionGenerator


class AsyncImageCaptionGenerator:
    """Handles asynchronous image caption generation.

    This class is designed to facilitate the generation of image captions
    asynchronously by delegating the workload to a process pool executor. It
    acts as a wrapper around a provided `ImageCaptionGenerator` instance,
    allowing non-blocking operations in environments where asynchronous
    programming is crucial.

    Attributes:
    executor (ProcessPoolExecutor): The executor used to offload tasks to a
        separate process pool.
    generator (ImageCaptionGenerator): The image caption generator instance
        responsible for the actual caption creation logic.

    """

    def __init__(
            self,
            executor: ProcessPoolExecutor,
            generator: ImageCaptionGenerator,
    ):
        self._executor = executor
        self._generator = generator

    async def generate_caption(self, file_bytes: BytesIO) -> str:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            self._executor,
            self._generator.get_caption_single_image,
            file_bytes,
        )
