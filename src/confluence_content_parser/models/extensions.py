from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from .base import ContentElement


class Panel(BaseModel):
    title: str | None = None
    border_style: str | None = None
    border_color: str | None = None
    title_bg_color: str | None = None
    title_color: str | None = None
    bg_color: str | None = None
    content: str = ""
    icon: str | None = None
    icon_id: str | None = None
    icon_text: str | None = None
    children: list[ContentElement] = Field(default_factory=list)


class Task(BaseModel):
    local_id: str = Field(..., alias="ac:local-id")
    task_id: str = Field(..., alias="ac:task-id")
    status: str = "incomplete"
    body: str = ""
    model_config = {"populate_by_name": True}


class I18nElement(BaseModel):
    key: str = Field(..., alias="at:key")
    model_config = {"populate_by_name": True}


class AdfExtension(BaseModel):
    extension_type: str | None = None
    extension_key: str | None = None
    parameters: dict[str, str] = Field(default_factory=dict)
    content: str = ""


class RichTextBody(BaseModel):
    content: str = ""


class PlainTextBody(BaseModel):
    content: str = ""


class AdfNode(BaseModel):
    type: str
    local_id: str | None = None
    attributes: dict[str, str] = Field(default_factory=dict)
    content: str = ""
    children: list[AdfNode] = Field(default_factory=list)


class AdfFallback(BaseModel):
    content: str = ""


class ViewFileMacro(BaseModel):
    name: str = ""
    version_at_save: str | None = None
    attachment_filename: str | None = None
    attachment_version_at_save: str | None = None


class GadgetMacro(BaseModel):
    url: str = ""
    layout: str | None = None
    local_id: str | None = None


class ExpandMacro(BaseModel):
    title: str = ""
    breakout_width: str | None = None
    content: str = ""
    children: list[ContentElement] = Field(default_factory=list)


class TocMacro(BaseModel):
    style: str | None = None
    local_id: str | None = None
