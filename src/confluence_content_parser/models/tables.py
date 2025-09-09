from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from .base import ContentElement


class Table(BaseModel):
    width: str | None = Field(None, alias="data-table-width")
    layout: str | None = Field(None, alias="data-layout")
    local_id: str | None = Field(None, alias="ac:local-id")
    cells: list[list[list["ContentElement"]]] = Field(default_factory=list)
    model_config = {"populate_by_name": True}
