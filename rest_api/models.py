from typing import Optional, Dict, Any

from pydantic import BaseModel


class ResponseModel(BaseModel):
    status: str
    status_code: int
    body: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    message: Optional[str] = None
