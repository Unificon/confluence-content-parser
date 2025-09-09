from pydantic import BaseModel


class Status(BaseModel):
    title: str
    colour: str


class DateElement(BaseModel):
    datetime: str
