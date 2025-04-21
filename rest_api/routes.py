import json
import os

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile, status
from pydantic import ValidationError

from domain.models import BaseResponse
from ioc.dependencies import user_service
from domain.dto import User, CreateUserDTO
from rest_api.models import ResponseModel
from services.user_service.user_service import UserService
from storage.client import S3ClientABC, get_s3_client

router = APIRouter()


@router.post("/upload_zip/")
async def upload_zip(
        file: UploadFile,
        user: str = Form(...),
        s3_client: S3ClientABC = Depends(get_s3_client),
):
    user_data = json.loads(user)
    user = User(**user_data)

    if not file.filename.endswith(".zip"):
        raise FileNotFoundError("File does not exist")

    temp_file_path = f"temp_{file.filename}"
    with open(temp_file_path, "wb") as buffer:
        buffer.write(await file.read())

    try:
        with open(temp_file_path, "rb") as file:
            files = file

        response = await upload_zip_utils(
            files=files,
            client=s3_client,
            user=user,
        )
    except json.JSONDecodeError as exception:
        return ResponseModel(
            status="error",
            status_code=exception.status_code if exception.status_code
            else status.HTTP_400_BAD_REQUEST,
            error=str(exception),
            message=f"Invalid JSON format. Failed to parse JSON user: {user}",
        ).dict()
    except ValidationError as exception:
        return ResponseModel(
            status="error",
            status_code=exception.status_code if exception.status_code
            else status.HTTP_400_BAD_REQUEST,
            error=str(exception),
            message=f"Validation error. Invalid user data user: {user}",
        ).dict()
    except Exception as exception:
        return ResponseModel(
            status="error",
            status_code=exception.status_code
            if exception.status_code else status.HTTP_400_BAD_REQUEST,
            error=str(exception),
        ).dict()
    else:
        return ResponseModel(
            status="success",
            body={"response": response},
            status_code=status.HTTP_201_CREATED,
            message=f"User data successfully uploaded to "
                    f"external service {s3_client.service_name}",
        ).model_dump()
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)


async def upload_zip_utils(files: dict, client: S3ClientABC,
                           user: User) -> dict:
    load_dotenv() #TODO remove in prod

    return await client.upload_zip(
        files=files,
        cloud_url=os.environ.get("TIMEWEB_CLOUD_URL"),
        user=user,
    )

@router.get("/payment_info/{user_id}")
async def payment_status(
        user_id: int | None,
        service: UserService = Depends(user_service),
):
    """Fetch the user's payment status from the database."""
    try:
        result = await service.payment_status(user_id)
        return BaseResponse.ok(data=bool(result), message="Check payment_info")
    except Exception as e:
        return BaseResponse.fail(
            error=f"Database error: {e!s}", message=f"status_code=500"
        )


@router.get("/users/{user_id}")
async def fetch_profile(
        user_id: int | None,
        service: UserService = Depends(user_service),
):
    try:
        result = await service.fetch_profile(user_id)
        return BaseResponse.ok(data=bool(result), message="Check user")
    except Exception as e:
        return BaseResponse.fail(
                error=f"Database error: {e!s}", message=f"status_code=500"
            )

@router.post("/add_user/")
async def add_user(
    user: CreateUserDTO,
    service: UserService = Depends(user_service),
):
    try:
        user = await service.add_user(
            tg_id=user.tg_id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            referral_link=user.referral_link,
            referrer_id=user.referrer_id,
        )
        return BaseResponse.ok(data=bool(user), message="Add user")

    except Exception as e:
        return BaseResponse.fail(
            error=f"Error processing request: {e!s}", message=f"status_code=500"
        )
