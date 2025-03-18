import asyncio
import json
import os

from fastapi import APIRouter, HTTPException, Depends, UploadFile, Form

from dotenv import load_dotenv
from pydantic import ValidationError

from models.api_model import StringsInput, User
from storage.client import S3ClientABC, get_s3_client

router = APIRouter()


@router.post("/upload_zip/")
async def upload_zip(
        file: UploadFile,
        user: str = Form(...),
        s3_client: S3ClientABC = Depends(get_s3_client)
):
    try:
        user_data = json.loads(user)
        user = User(**user_data)
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Invalid JSON format",
                "message": f"Failed to parse JSON: {str(e)}"
            }
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=422,
            detail={
                "error": "Validation error",
                "message": "Invalid user data",
                "errors": e.errors()
            }
        )

    if not file.filename.endswith(".zip"):
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Invalid file format",
                "message": "File must be a ZIP archive",
            }
        )

    temp_file_path = f"temp_{file.filename}"
    with open(temp_file_path, "wb") as buffer:
        buffer.write(await file.read())

    try:
        with open(temp_file_path, "rb") as file:
            files = file
        #todo обработка ошибок при загрузке файлов в S3
        response = await upload_zip_utils(
            files=files,
            client=s3_client,
            user=user
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error while uploading to external service {str(e)}")
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
    return {
        "message": "Файл и данные пользователя успешно отправлены",
        "response": response
    }


async def upload_zip_utils(files: dict, client: S3ClientABC, user: User) -> dict:
    load_dotenv() #todo remove in prod
    return await client.upload_zip(
        files=files,
        cloud_url=os.environ.get("TIMEWEB_CLOUD_URL"),
        user=user
    )
