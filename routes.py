import base64

from fastapi import Response, APIRouter
from pydantic import BaseModel
from PIL import Image
import io

router = APIRouter()


class ImageData(BaseModel):
    name: str
    data: str


def generate_image_variation(image_bytes) -> bytes:
    try:
        image = Image.open(io.BytesIO(image_bytes))
        resized_image = image.resize((100, 40))

        return image_bytes
    except Exception as e:
        print(f"Ошибка при генерации изображения: {e}")
        return None


@router.post("/process_image/")
async def process_image(image: ImageData):
    try:
        image_bytes = base64.b64decode(image.data)
        modified_image = generate_image_variation(image_bytes)

        if modified_image:
            return Response(content=modified_image)
        else:
            return {"error": "Не удалось обработать изображение"}
    except Exception as e:
        return {"error": str(e)}
