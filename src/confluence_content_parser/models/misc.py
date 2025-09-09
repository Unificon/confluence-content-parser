from pydantic import BaseModel, Field


class InlineComment(BaseModel):
    ref: str = Field(..., alias="ac:ref")
    text: str = ""
    model_config = {"populate_by_name": True}


class Emoticon(BaseModel):
    name: str = Field(..., alias="ac:name")
    emoji_shortname: str | None = Field(None, alias="ac:emoji-shortname")
    emoji_id: str | None = Field(None, alias="ac:emoji-id")
    emoji_fallback: str | None = Field(None, alias="ac:emoji-fallback")
    model_config = {"populate_by_name": True}


class Placeholder(BaseModel):
    type: str | None = Field(None, alias="ac:type")
    text: str = ""
    model_config = {"populate_by_name": True}
