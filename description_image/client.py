import asyncio
import os
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration
from typing import List, Dict
from io import BytesIO


class ImageDescriptor:
    def __init__(self):
        self.processor = BlipProcessor.from_pretrained(
            "Salesforce/blip-image-captioning-base")
        self.model = BlipForConditionalGeneration.from_pretrained(
            "Salesforce/blip-image-captioning-base")

    async def get_caption_single_image(self, file_bytes) -> str:
        try:
            # Load and process image
            raw_image = Image.open(BytesIO(file_bytes)).convert('RGB')
            # conditional image captioning
            inputs = self.processor(raw_image, return_tensors="pt")

            # Generate caption
            out = self.model.generate(**inputs)
            caption = self.processor.decode(out[0], skip_special_tokens=True)

            return caption

        except Exception as e:
            return f"Error processing image: {str(e)}"

    async def process_single_image(self, image_path: str) -> str:
        try:
            # Load and process image
            raw_image = Image.open(image_path).convert('RGB')
            # conditional image captioning
            inputs = self.processor(raw_image, return_tensors="pt")

            # Generate caption
            out = self.model.generate(**inputs)
            caption = self.processor.decode(out[0], skip_special_tokens=True)

            return caption

        except Exception as e:
            return f"Error processing image: {str(e)}"

    async def get_caption_images(self, image_paths: List[str]) -> Dict[str, str]:
        # Create tasks for each image
        tasks = [
            asyncio.create_task(self.process_single_image(path))
            for path in image_paths
        ]

        # Wait for all tasks to complete
        captions = await asyncio.gather(*tasks)

        # Create dictionary with image names as keys and captions as values
        return {
            os.path.basename(path): caption
            for path, caption in zip(image_paths, captions)
        }

