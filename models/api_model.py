from pydantic import BaseModel


class StringsInput(BaseModel):
    strings: list[str]


class User(BaseModel):
    id: int | str
