from io import BytesIO

from PIL import Image
from transformers import BlipForConditionalGeneration, BlipProcessor


class ImageCaptionGenerator:
    def __init__(self):
        self.processor = BlipProcessor.from_pretrained(
            "Salesforce/blip-image-captioning-base")
        self.model = BlipForConditionalGeneration.from_pretrained(
            "Salesforce/blip-image-captioning-base")

    def get_caption_single_image(self, file_bytes: BytesIO) -> str:
        try:
            # Load and process image
            raw_image = Image.open(file_bytes).convert("RGB")
            # conditional image captioning
            inputs = self.processor(raw_image, return_tensors="pt")

            # Generate caption
            out = self.model.generate(**inputs)
            caption = self.processor.decode(out[0], skip_special_tokens=True)

            return caption

        except Exception as e:
            return f"Error processing image: {e!s}"

    def process_single_image(self, image_path: str) -> str:
        try:
            # Load and process image
            raw_image = Image.open(image_path).convert("RGB")
            # conditional image captioning
            inputs = self.processor(raw_image, return_tensors="pt")

            # Generate caption
            out = self.model.generate(**inputs)
            caption = self.processor.decode(out[0], skip_special_tokens=True)

            return caption

        except Exception as e:
            return f"Error processing image: {e!s}"

