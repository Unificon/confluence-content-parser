from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from .base import ContentElement


class LayoutCell(BaseModel):
    content: list[ContentElement] = Field(default_factory=list)


class LayoutSection(BaseModel):
    type: str = Field(..., alias="ac:type")
    breakout_mode: str | None = Field(None, alias="ac:breakout-mode")
    breakout_width: str | None = Field(None, alias="ac:breakout-width")
    cells: list[LayoutCell] = Field(default_factory=list)
    model_config = {"populate_by_name": True}
