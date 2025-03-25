import json
import os

from fastapi import APIRouter, HTTPException, Depends, UploadFile, Form, status

from dotenv import load_dotenv
from pydantic import ValidationError

from models.api_model import User
from rest_api.models import ResponseModel
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
    except json.JSONDecodeError as exp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ResponseModel(
                status="error",
                error=str(exp),
                status_code=status.HTTP_400_BAD_REQUEST,
                message=f"Invalid JSON format. Failed to parse JSON user: {user}"
            ).dict()
        )
    except ValidationError as exp:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=ResponseModel(
                status="error",
                error=str(exp),
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                message=f"Validation error. Invalid user data user: {user}"
            ).dict()
        )

    if not file.filename.endswith(".zip"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ResponseModel(
                status="error",
                error="",
                status_code=status.HTTP_400_BAD_REQUEST,
                message=f"Invalid file format. File must be a ZIP archive user: {user}"
            ).dict()
        )

    temp_file_path = f"temp_{file.filename}"
    with open(temp_file_path, "wb") as buffer:
        buffer.write(await file.read())

    try:
        with open(temp_file_path, "rb") as file:
            files = file

        response = await upload_zip_utils(
            files=files,
            client=s3_client,
            user=user
        )
    except Exception as exception:
        return ResponseModel(
            status="error",
            status_code=exception.status_code if exception.status_code else status.HTTP_400_BAD_REQUEST,
            error=str(exception)
        ).dict()
    else:
        return ResponseModel(
            status="success",
            body={"response": response},
            status_code=status.HTTP_201_CREATED,
            message=f"User data successfully uploaded to external service {s3_client.service_name}"
        ).dict()
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)


async def upload_zip_utils(files: dict, client: S3ClientABC, user: User) -> dict:
    load_dotenv() #todo remove in prod

    return await client.upload_zip(
        files=files,
        cloud_url=os.environ.get("TIMEWEB_CLOUD_URL"),
        user=user
    )
