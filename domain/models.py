from typing import Generic, TypeVar, Optional
from pydantic import BaseModel

T = TypeVar("T")

class BaseResponse(BaseModel, Generic[T]):
    success: bool = False
    data: Optional[T] = None
    error: Optional[str] = None
    message: Optional[str] = None

    @classmethod
    def ok(cls, data: T, message: str = None) -> "BaseResponse[T]":
        return cls(success=True, data=data, message=message)

    @classmethod
    def fail(cls, error: str, message: str = None) -> "BaseResponse[None]":
        return cls(success=False, error=error, message=message)