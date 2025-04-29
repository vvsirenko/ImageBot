import datetime
import uuid
from typing import Annotated, Optional

from pydantic import BaseModel, PlainValidator, Field


ImageCount = Annotated[
    int,
    PlainValidator(
        lambda v: v if isinstance(v, int) and v >= 0
        else ValueError("PhotoCredits must be a positive integer")
    )
]

Price = Annotated[
    int,
    PlainValidator(
        lambda v: v if isinstance(v, int) and v >= 0
        else ValueError("PhotoCredits must be a positive integer")
    )
]

Name = Annotated[
    str,
    PlainValidator(
        lambda v: v if isinstance(v, str)
        else ValueError("Name must be a string"))
]


class Subscription(BaseModel):
    id: uuid.UUID = Field(default_factory=lambda: uuid.uuid4())
    name: Optional[Name] = Field(default=None)
    image_count: Optional[ImageCount] = Field(default=None)
    price: Optional[Price] = Field(default=None)

    def to_dict(self) -> dict:
        return self.dict(exclude_none=True)

