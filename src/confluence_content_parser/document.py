from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from .nodes import Node


class ConfluenceDocument(BaseModel):
    """A parsed Confluence document with convenient access to content."""

    root: Node | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    @property
    def text(self) -> str:
        """Get all text content from the document with proper line breaks."""
        if not self.root:
            return ""

        parts = []
        for child in self.root.get_children():
            text = child.to_text().strip()
            if text:
                parts.append(text)

        return "\n\n".join(parts)

    def find_all(self, node_type: type[Node] | None = None) -> list[Node]:
        """Find all nodes of a specific type in the document, or all nodes if no type specified."""
        return self.root.find_all(node_type) if self.root else []

    def walk(self) -> list[Node]:
        """Get all nodes in the document."""
        return list(self.root.walk()) if self.root else []
