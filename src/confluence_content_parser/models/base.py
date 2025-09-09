from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from .extensions import (
        AdfExtension,
        AdfFallback,
        AdfNode,
        ExpandMacro,
        GadgetMacro,
        I18nElement,
        Panel,
        Task,
        TocMacro,
        ViewFileMacro,
    )
    from .layout import LayoutCell, LayoutSection
    from .links import Link
    from .macros import (
        AnchorMacro,
        AttachmentsMacro,
        ChildrenDisplayMacro,
        CodeBlock,
        ExcerptIncludeMacro,
        ExcerptMacro,
        JiraMacro,
        NotificationMacro,
        PagePropertiesMacro,
        PagePropertiesReportMacro,
        StructuredMacro,
    )
    from .media import Image
    from .metadata import DateElement, Status
    from .misc import Emoticon, InlineComment, Placeholder
    from .tables import Table
    from .tasks import (
        DecisionList,
        TaskElement,
        TaskList,
        TaskListContainer,
    )


class ContentElement(BaseModel):
    id: str | None = None
    type: str
    path: list[str | int] = Field(default_factory=list)
    sibling_index: int | None = None
    heading_scope_id: str | None = None
    list_scope: dict[str, Any] = Field(default_factory=dict)
    layout_scope: dict[str, Any] = Field(default_factory=dict)
    text: str | None = None
    attributes: dict[str, Any] = Field(default_factory=dict)
    children: list[ContentElement] = Field(default_factory=list)

    link: Link | None = None
    macro: StructuredMacro | None = None
    table: Table | None = None
    layout_section: LayoutSection | None = None
    layout_cell: LayoutCell | None = None
    inline_comment: InlineComment | None = None
    status: Status | None = None
    emoticon: Emoticon | None = None
    date: DateElement | None = None
    decision_list: DecisionList | None = None
    task_list: TaskList | None = None
    placeholder: Placeholder | None = None
    image: Image | None = None
    code_block: CodeBlock | None = None
    panel: Panel | None = None
    task: Task | None = None
    i18n: I18nElement | None = None
    adf_extension: AdfExtension | None = None
    task_element: TaskElement | None = None
    task_list_container: TaskListContainer | None = None
    adf_node: AdfNode | None = None
    adf_fallback: AdfFallback | None = None
    view_file_macro: ViewFileMacro | None = None
    gadget_macro: GadgetMacro | None = None
    expand_macro: ExpandMacro | None = None
    toc_macro: TocMacro | None = None
    jira_macro: JiraMacro | None = None
    notification_macro: NotificationMacro | None = None
    anchor_macro: AnchorMacro | None = None
    excerpt_macro: ExcerptMacro | None = None
    excerpt_include_macro: ExcerptIncludeMacro | None = None
    page_properties_macro: PagePropertiesMacro | None = None
    page_properties_report_macro: PagePropertiesReportMacro | None = None
    children_display_macro: ChildrenDisplayMacro | None = None
    attachments_macro: AttachmentsMacro | None = None

    def iter(self):
        yield self
        for child in self.children:
            yield from child.iter()

    def find_all(self, *, type: str | None = None, kind: str | None = None) -> list["ContentElement"]:
        results: list[ContentElement] = []
        for el in self.iter():
            if (type is None or el.type == type) and (kind is None or el.kind == kind):
                results.append(el)
        return results

    def text_normalized(self) -> str:
        parts: list[str] = []
        if self.text:
            parts.append(self.text)
        for child in self.children:
            t = child.text_normalized()
            if t:
                parts.append(t)
        return " ".join(s for s in (p.strip() for p in parts) if s)

    @property
    def kind(self) -> str | None:
        if self.type in {"h1","h2","h3","h4","h5","h6"}:
            return "heading"
        if self.type in {"ul","ol"}:
            return "list"
        if self.type == "li":
            return "list_item"
        if self.type == "hr":
            return "hr"
        if self.type == "br":
            return "br"
        if self.code_block is not None:
            return "code_block"
        if self.link is not None:
            return "link"
        if self.image is not None:
            return "image"
        if self.table is not None:
            return "table"
        if self.panel is not None:
            return "macro:panel"
        if self.notification_macro is not None:
            return "macro:notification"
        if self.jira_macro is not None:
            return "macro:jira"
        if self.toc_macro is not None:
            return "macro:toc"
        if self.expand_macro is not None:
            return "macro:expand"
        if self.view_file_macro is not None:
            return "macro:view_file"
        if self.gadget_macro is not None:
            return "macro:gadget"
        if self.anchor_macro is not None:
            return "macro:anchor"
        if self.excerpt_macro is not None:
            return "macro:excerpt"
        if self.excerpt_include_macro is not None:
            return "macro:excerpt_include"
        if self.page_properties_macro is not None:
            return "macro:page_properties"
        if self.page_properties_report_macro is not None:
            return "macro:page_properties_report"
        if self.children_display_macro is not None:
            return "macro:children_display"
        if self.attachments_macro is not None:
            return "macro:attachments"
        if self.adf_node is not None:
            return "adf_node"
        if self.adf_fallback is not None:
            return "adf_fallback"
        if self.type == "p":
            return "paragraph"
        if self.type == "layout":
            return "layout"
        if self.type == "layout_section":
            return "layout_section"
        if self.type == "layout_cell":
            return "layout_cell"
        if self.placeholder is not None:
            return "placeholder"
        if self.inline_comment is not None:
            return "inline_comment"
        if self.status is not None:
            return "status"
        if self.date is not None:
            return "date"
        return None


class ConfluenceDocument(BaseModel):
    title: str | None = None
    content: list[ContentElement] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
