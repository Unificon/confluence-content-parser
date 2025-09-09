from .base import ConfluenceDocument, ContentElement
from .extensions import (
    AdfExtension,
    AdfFallback,
    AdfNode,
    ExpandMacro,
    GadgetMacro,
    I18nElement,
    Panel,
    PlainTextBody,
    RichTextBody,
    Task,
    TocMacro,
    ViewFileMacro,
)
from .layout import LayoutCell, LayoutSection
from .links import AttachmentReference, Link, PageReference, UrlReference, UserReference, BlogPostReference, SpaceReference, ContentEntityReference, ShortcutReference
from .macros import CodeBlock, JiraMacro, NotificationMacro, StructuredMacro, AnchorMacro, ExcerptMacro, ExcerptIncludeMacro, PagePropertiesMacro, PagePropertiesReportMacro, ChildrenDisplayMacro, AttachmentsMacro
from .media import Image
from .metadata import DateElement, Status
from .misc import Emoticon, InlineComment, Placeholder
from .tables import Table
from .tasks import DecisionItem, DecisionList, TaskElement, TaskItem, TaskList, TaskListContainer

# Rebuild models to resolve forward references
LayoutSection.model_rebuild()
LayoutCell.model_rebuild()
ContentElement.model_rebuild()
TaskList.model_rebuild()
AdfNode.model_rebuild()
Panel.model_rebuild()
ExpandMacro.model_rebuild()
Table.model_rebuild()
ExcerptMacro.model_rebuild()
PagePropertiesMacro.model_rebuild()

__all__ = [
    "ConfluenceDocument",
    "ContentElement",
    "Link",
    "StructuredMacro",
    "Table",
    "LayoutSection",
    "LayoutCell",
    "UserReference",
    "PageReference",
    "AttachmentReference",
    "UrlReference",
    "BlogPostReference",
    "SpaceReference",
    "ContentEntityReference",
    "ShortcutReference",
    "Image",
    "InlineComment",
    "Status",
    "Emoticon",
    "DateElement",
    "DecisionList",
    "DecisionItem",
    "TaskList",
    "TaskItem",
    "TaskElement",
    "TaskListContainer",
    "Placeholder",
    "CodeBlock",
    "Panel",
    "Task",
    "I18nElement",
    "AdfExtension",
    "AdfNode",
    "AdfFallback",
    "ViewFileMacro",
    "GadgetMacro",
    "ExpandMacro",
    "TocMacro",
    "JiraMacro",
    "NotificationMacro",
    "AnchorMacro",
    "ExcerptMacro",
    "ExcerptIncludeMacro",
    "PagePropertiesMacro",
    "PagePropertiesReportMacro",
    "ChildrenDisplayMacro",
    "AttachmentsMacro",
    "RichTextBody",
    "PlainTextBody",
    "ElementKind",
]
