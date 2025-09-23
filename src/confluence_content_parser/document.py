from __future__ import annotations

from typing import Any, TypeVar, overload

from pydantic import BaseModel, Field

from .nodes import Node

T1 = TypeVar("T1", bound=Node)
T2 = TypeVar("T2", bound=Node)
T3 = TypeVar("T3", bound=Node)
T4 = TypeVar("T4", bound=Node)
T5 = TypeVar("T5", bound=Node)


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

    @overload
    def find_all(self) -> list[Node]: ...

    @overload
    def find_all(self, node_type: type[T1]) -> list[T1]: ...

    @overload
    def find_all(self, t1: type[T1], t2: type[T2]) -> tuple[list[T1], list[T2]]: ...

    @overload
    def find_all(self, t1: type[T1], t2: type[T2], t3: type[T3]) -> tuple[list[T1], list[T2], list[T3]]: ...

    @overload
    def find_all(
        self, t1: type[T1], t2: type[T2], t3: type[T3], t4: type[T4]
    ) -> tuple[list[T1], list[T2], list[T3], list[T4]]: ...

    @overload
    def find_all(
        self, t1: type[T1], t2: type[T2], t3: type[T3], t4: type[T4], t5: type[T5]
    ) -> tuple[list[T1], list[T2], list[T3], list[T4], list[T5]]: ...

    def find_all(self, *node_types) -> Any:  # type: ignore[no-untyped-def,misc]
        """Find all nodes of specific type(s) in the document with modern variadic generics.

        Args:
            *node_types: Either no arguments (all nodes), a single node class, or multiple node classes.

        Returns:
            - No arguments: list[Node] (all nodes)
            - Single type: list[T] where T is the requested type
            - Multiple types: tuple of lists with proper typing for each type

        Examples:
            # All nodes
            all_nodes = document.find_all()

            # Single type
            headings = document.find_all(HeadingElement)

            # Multiple types
            headings, panels = document.find_all(HeadingElement, PanelMacro)
        """
        if self.root:
            return self.root.find_all(*node_types)
        else:
            if len(node_types) == 0:
                return []
            elif len(node_types) == 1:
                return []
            else:
                return tuple([] for _ in node_types)

    def walk(self) -> list[Node]:
        """Get all nodes in the document."""
        return list(self.root.walk()) if self.root else []
