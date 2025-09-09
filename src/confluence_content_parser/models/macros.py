from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from .base import ContentElement


class Parameter(BaseModel):
    name: str = Field(..., alias="ac:name")
    value: str
    model_config = {"populate_by_name": True}


class StructuredMacro(BaseModel):
    name: str
    macro_id: str = Field(..., alias="ac:macro-id")
    schema_version: str | None = Field(None, alias="ac:schema-version")
    parameters: dict[str, str] = Field(default_factory=dict)
    body: str | None = None
    layout: str | None = Field(None, alias="data-layout")
    model_config = {"populate_by_name": True}


class CodeBlock(BaseModel):
    language: str | None = None
    title: str | None = None
    collapse: bool | None = None
    linenumbers: bool | None = None
    theme: str | None = None
    breakout_mode: str | None = None
    breakout_width: str | None = None
    content: str = ""


class JiraMacro(BaseModel):
    key: str = ""
    server_id: str = ""
    server: str = ""


class NotificationMacro(BaseModel):
    macro_type: str  # info, warning, note, tip
    content: str = ""


class AnchorMacro(BaseModel):
    anchor: str = ""


class ExcerptMacro(BaseModel):
    hidden: bool = False
    atlassian_macro_output_type: str | None = Field(None, alias="ac:macro-output-type")
    body: str = ""
    children: list["ContentElement"] = Field(default_factory=list)
    model_config = {"populate_by_name": True}


class ExcerptIncludeMacro(BaseModel):
    page: str = ""


class PagePropertiesMacro(BaseModel):
    id: str | None = None
    hidden: bool = False
    body: str = ""
    children: list["ContentElement"] = Field(default_factory=list)


class PagePropertiesReportMacro(BaseModel):
    id: str | None = None
    labels: list[str] = Field(default_factory=list)
    space_key: str | None = None


class ChildrenDisplayMacro(BaseModel):
    depth: int | None = None
    excerpt: str | None = None
    sort: str | None = None
    reverse: bool | None = None
    parent: str | None = None


class AttachmentsMacro(BaseModel):
    patterns: list[str] = Field(default_factory=list)
    page: str | None = None
