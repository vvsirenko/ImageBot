"""Глобальные сущности."""
import concurrent.futures

from libs.image_caption_generator.image_caption_generator import ImageCaptionGenerator
from libs.image_caption_generator.main import AsyncImageCaptionGenerator
from libs.zip_maker.main import ZipCreator

executor = concurrent.futures.ProcessPoolExecutor(max_workers=10)
image_caption_generator = AsyncImageCaptionGenerator(executor=executor, generator=ImageCaptionGenerator())
zip_creator = ZipCreator(executor=executor)
