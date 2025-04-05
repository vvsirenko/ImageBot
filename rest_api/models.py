from datetime import datetime
from typing import Any, Final

from pydantic import BaseModel


class ResponseModel(BaseModel):
    status: str
    status_code: int
    body: dict[str, Any] | None = None
    error: str | None = None
    message: str | None = None


DATE_TO_STRING_FORMAT: Final[str] = "%Y-%m-%dT%H:%M:%S%z"


class BaseMessageModel(BaseModel):
    success: bool = True
    meta: dict[str, str] = dict()

    def fill_meta(self):
        self.meta.update(
            {"date": datetime.now().strftime(DATE_TO_STRING_FORMAT)},
        )


class SuccessMessage(BaseMessageModel):
    body: dict = dict()


class ErrorMessage(BaseMessageModel):
    error: dict = dict()

    def __init__(self, exception, **data):
        super().__init__(**data)
        self.success = False
        self.error = self.create_error_data(exception)
        self.fill_meta()

    @staticmethod
    def create_error_data(exception: Exception) -> dict:
        return {
            "code": getattr(exception, "code", "503"),
            "title": getattr(exception, "title", "EXCEPTION"),
            "text": exception.__str__(),
            "description": getattr(exception, "description", "internal server error"),
        }
