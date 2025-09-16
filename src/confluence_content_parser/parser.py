from __future__ import annotations

import xml.etree.ElementTree as ET
from collections.abc import Callable, Iterator

from .document import ConfluenceDocument
from .nodes import (
    AnchorMacro,
    AttachmentsMacro,
    CodeMacro,
    DecisionList,
    DecisionListItem,
    DecisionListItemState,
    DetailsMacro,
    Emoticon,
    ExcerptIncludeMacro,
    ExcerptMacro,
    ExpandMacro,
    Fragment,
    HeadingElement,
    HeadingType,
    Image,
    IncludeMacro,
    JiraMacro,
    LayoutCell,
    LayoutElement,
    LayoutSection,
    LayoutSectionType,
    LinkElement,
    LinkType,
    ListElement,
    ListItem,
    ListType,
    Node,
    PanelMacro,
    PanelMacroType,
    PlaceholderElement,
    ProfileMacro,
    ResourceIdentifier,
    ResourceIdentifierType,
    StatusMacro,
    Table,
    TableCell,
    TableRow,
    TaskListItemStatus,
    TasksReportMacro,
    Text,
    TextBreakElement,
    TextBreakType,
    TextEffectElement,
    TextEffectType,
    Time,
    TocMacro,
    ViewFileMacro,
    ViewPdfMacro,
)


class ParsingError(Exception):
    """Raised when parsing fails with diagnostics."""

    def __init__(self, diagnostics: list[str]):
        self.diagnostics = diagnostics
        super().__init__("; ".join(diagnostics) if diagnostics else "ParsingError")


class ConfluenceParser:
    """Efficient Confluence storage-format XML parser with generic element handling."""

    NS_AC = "http://www.atlassian.com/schema/confluence/4/ac/"
    NS_RI = "http://www.atlassian.com/schema/confluence/4/ri/"
    NS_AT = "http://www.atlassian.com/schema/confluence/4/at/"

    def __init__(self, *, raise_on_finish: bool = True):
        self.diagnostics: list[str] = []
        self.raise_on_finish = raise_on_finish
        self._skipped_elements = {"colgroup", "col", "adf-fallback", "inline-comment-marker"}
        self._element_parsers: dict[str, Callable[[ET.Element], Node | None]] = {
            "macro": self._parse_macro,
            "structured-macro": self._parse_structured_macro,
            "layout": self._parse_layout,
            "layout-section": self._parse_layout_section,
            "layout-cell": self._parse_layout_cell,
            "h1": self._parse_heading,
            "h2": self._parse_heading,
            "h3": self._parse_heading,
            "h4": self._parse_heading,
            "h5": self._parse_heading,
            "h6": self._parse_heading,
            "strong": self._parse_text_effect,
            "em": self._parse_text_effect,
            "u": self._parse_text_effect,
            "del": self._parse_text_effect,
            "code": self._parse_text_effect,
            "sub": self._parse_text_effect,
            "sup": self._parse_text_effect,
            "blockquote": self._parse_text_effect,
            "span": self._parse_text_effect,
            "p": self._parse_text_break,
            "br": self._parse_text_break,
            "hr": self._parse_text_break,
            "ul": self._parse_list,
            "ol": self._parse_list,
            "li": self._parse_list_item,
            "task-list": self._parse_list,
            "task": self._parse_list_item,
            "link": self._parse_link,
            "link-body": self._parse_link_body,
            "a": self._parse_external_link,
            "image": self._parse_image,
            "emoticon": self._parse_emoticon,
            "placeholder": self._parse_placeholder,
            "time": self._parse_time,
            "page": self._parse_resource_identifier,
            "blog-post": self._parse_resource_identifier,
            "attachment": self._parse_resource_identifier,
            "url": self._parse_resource_identifier,
            "shortcut": self._parse_resource_identifier,
            "user": self._parse_resource_identifier,
            "space": self._parse_resource_identifier,
            "content-entity": self._parse_resource_identifier,
            "table": self._parse_table,
            "tbody": self._parse_table_body,
            "tr": self._parse_table_row,
            "th": self._parse_table_cell,
            "td": self._parse_table_cell,
            "adf-extension": self._parse_adf_extension,
        }
        self._macro_parsers: dict[str, Callable[[ET.Element], Node | None]] = {
            "panel": self._parse_panel_macro,
            "tip": self._parse_panel_macro,
            "note": self._parse_panel_macro,
            "warning": self._parse_panel_macro,
            "info": self._parse_panel_macro,
            "code": self._parse_code_macro,
            "details": self._parse_details_macro,
            "expand": self._parse_expand_macro,
            "status": self._parse_status_macro,
            "toc": self._parse_toc_macro,
            "jira": self._parse_jira_macro,
            "include": self._parse_include_macro,
            "tasks-report-macro": self._parse_tasks_report_macro,
            "excerpt-include": self._parse_excerpt_include_macro,
            "attachments": self._parse_attachments_macro,
            "viewpdf": self._parse_viewpdf_macro,
            "view-file": self._parse_view_file_macro,
            "profile": self._parse_profile_macro,
            "anchor": self._parse_anchor_macro,
            "excerpt": self._parse_excerpt_macro,
        }

    def parse(self, content: str) -> ConfluenceDocument:
        """Parse Confluence storage-format XML into a ConfluenceDocument."""
        self.diagnostics.clear()

        try:
            content = self._normalize_content(content)
            root_element = ET.fromstring(content)
        except ET.ParseError as e:
            self.diagnostics.append(f"XML parsing failed: {e}")
            return ConfluenceDocument(metadata={"diagnostics": self.diagnostics})

        children = self._parse_children(root_element)
        root_node = self._consolidate_root(children)

        if self.raise_on_finish and self.diagnostics:
            raise ParsingError(self.diagnostics[:])

        return ConfluenceDocument(root=root_node, metadata={"diagnostics": self.diagnostics})

    def _normalize_content(self, content: str) -> str:
        """Add namespace declarations and entity definitions to ensure proper XML parsing."""
        content = content.strip()

        content = self._fix_unicode_surrogates(content)

        return f"""<?xml version="1.0" encoding="UTF-8"?>
        <!DOCTYPE root [
            <!ENTITY nbsp "&#160;">
            <!ENTITY ndash "&#8211;">
            <!ENTITY mdash "&#8212;">
            <!ENTITY ldquo "&#8220;">
            <!ENTITY rdquo "&#8221;">
            <!ENTITY lsquo "&#8216;">
            <!ENTITY rsquo "&#8217;">
            <!ENTITY hellip "&#8230;">
            <!ENTITY copy "&#169;">
            <!ENTITY reg "&#174;">
            <!ENTITY trade "&#8482;">
            <!ENTITY zwj "&#8205;">
            <!ENTITY zwnj "&#8204;">
        ]>
        <root xmlns:ac="{self.NS_AC}"
            xmlns:ri="{self.NS_RI}"
            xmlns:at="{self.NS_AT}">
            {content}
        </root>"""

    def _fix_unicode_surrogates(self, content: str) -> str:
        """Fix Unicode surrogate characters that can cause XML parsing issues."""
        try:
            content.encode("utf-8")
            return content
        except UnicodeEncodeError:
            result = []
            i = 0
            while i < len(content):
                char = content[i]
                try:
                    char.encode("utf-8")
                    result.append(char)
                except UnicodeEncodeError:
                    pass
                i += 1
            return "".join(result)

    def _consolidate_root(self, children: list[Node]) -> Node | None:
        """Convert parsed children into appropriate root node structure."""
        if len(children) == 0:
            return None
        elif len(children) == 1:
            return children[0]
        else:
            return Fragment(children=children)

    def _parse_children(self, element: ET.Element) -> list[Node]:
        """Parse all children of an element into nodes."""
        nodes: list[Node] = []

        if element.text and element.text.strip():
            nodes.append(Text(text=element.text.strip()))

        for child in element:
            node = self._parse_element(child)
            if node:
                nodes.append(node)

            if child.tail and child.tail.strip():
                nodes.append(Text(text=child.tail.strip()))

        return nodes

    def _parse_element(self, element: ET.Element) -> Node | None:
        """Parse a single element into appropriate node type."""
        tag = self._get_tag_name(element)

        if tag in self._skipped_elements:
            return None

        parser = self._element_parsers.get(tag)
        if parser:
            return parser(element)

        self.diagnostics.append(f"unknown_element:{tag}")
        return None

    def _parse_layout(self, element: ET.Element) -> LayoutElement:
        """Parse ac:layout element."""
        return LayoutElement(children=self._parse_children(element))

    def _parse_layout_section(self, element: ET.Element) -> LayoutSection:
        """Parse ac:layout-section element."""
        section_type_str = self._get_attr(element, "type") or "single"
        section_type = LayoutSectionType(section_type_str)

        breakout_mode = self._get_attr(element, "breakout-mode")
        breakout_width = self._get_attr(element, "breakout-width")

        return LayoutSection(
            section_type=section_type,
            breakout_mode=breakout_mode,
            breakout_width=breakout_width,
            children=self._parse_children(element),
        )

    def _parse_layout_cell(self, element: ET.Element) -> LayoutCell:
        """Parse ac:layout-cell element."""
        return LayoutCell(children=self._parse_children(element))

    def _parse_heading(self, element: ET.Element) -> HeadingElement:
        """Parse heading elements (h1, h2, h3, h4, h5, h6)."""
        tag = self._get_tag_name(element)
        heading_type = HeadingType(tag)
        styles = self._parse_css_styles(element)
        return HeadingElement(type=heading_type, styles=styles, children=self._parse_children(element))

    def _parse_text_effect(self, element: ET.Element) -> TextEffectElement:
        """Parse text effect elements (strong, em, span, etc.)."""
        tag = self._get_tag_name(element)
        effect_type = TextEffectType(tag)

        styles = self._parse_css_styles(element)

        return TextEffectElement(type=effect_type, styles=styles, children=self._parse_children(element))

    def _parse_text_break(self, element: ET.Element) -> TextBreakElement:
        """Parse text break elements (p, br, hr)."""
        tag = self._get_tag_name(element)
        break_type = TextBreakType(tag)

        if break_type == TextBreakType.PARAGRAPH:
            styles = self._parse_css_styles(element)
            return TextBreakElement(type=break_type, styles=styles, children=self._parse_children(element))
        else:
            return TextBreakElement(type=break_type)

    def _parse_list(self, element: ET.Element) -> ListElement:
        """Parse list elements (ul, ol, task-list)."""
        tag = self._get_tag_name(element)
        list_type = ListType(tag)

        start = None
        if list_type == ListType.ORDERED:
            start_attr = self._get_attr(element, "start")
            if start_attr:
                try:
                    start = int(start_attr)
                except ValueError:
                    pass

        return ListElement(type=list_type, start=start, children=self._parse_children(element))

    def _parse_list_item(self, element: ET.Element) -> ListItem:
        """Parse list item elements (li, ac:task)."""
        tag = self._get_tag_name(element)

        if tag == "task":
            task_id = None
            uuid = None
            status = TaskListItemStatus.INCOMPLETE
            children = []

            for child in element:
                child_tag = self._get_tag_name(child)
                if child_tag == "task-id":
                    task_id = self._extract_text_content(child)
                elif child_tag == "task-uuid":
                    uuid = self._extract_text_content(child)
                elif child_tag == "task-status":
                    status_text = self._extract_text_content(child)
                    status = TaskListItemStatus(status_text)
                elif child_tag == "task-body":
                    children = self._parse_children(child)

            return ListItem(task_id=task_id, uuid=uuid, status=status, children=children)
        else:
            return ListItem(children=self._parse_children(element))

    def _parse_external_link(self, element: ET.Element) -> LinkElement:
        """Parse external <a> links."""
        href = self._get_attr(element, "href")

        if href and href.startswith("mailto:"):
            link_type = LinkType.MAILTO
        else:
            link_type = LinkType.EXTERNAL

        return LinkElement(type=link_type, href=href, children=self._parse_children(element))

    def _parse_link(self, element: ET.Element) -> LinkElement:
        """Parse ac:link elements."""
        anchor = self._get_attr(element, "anchor")

        children = self._parse_children(element)

        link_type = LinkType.EXTERNAL
        if anchor:
            link_type = LinkType.ANCHOR
        else:
            for child in children:
                if hasattr(child, "type") and hasattr(child.type, "value"):
                    if child.type.value == "page":
                        link_type = LinkType.PAGE
                        break
                    elif child.type.value == "blog-post":
                        link_type = LinkType.BLOG_POST
                        break
                    elif child.type.value == "user":
                        link_type = LinkType.USER
                        break
                    elif child.type.value == "space":
                        link_type = LinkType.SPACE
                        break
                    elif child.type.value == "attachment":
                        link_type = LinkType.ATTACHMENT
                        break

        return LinkElement(type=link_type, anchor=anchor, children=children)

    def _parse_link_body(self, element: ET.Element) -> Fragment:
        """Parse ac:link-body elements as fragment containers for rich content."""
        return Fragment(children=self._parse_children(element))

    def _parse_image(self, element: ET.Element) -> Image:
        """Parse ac:image elements."""
        src = self._get_attr(element, "src")
        alt = self._get_attr(element, "alt")
        title = self._get_attr(element, "title")
        width = self._get_attr(element, "width")
        height = self._get_attr(element, "height")
        alignment = self._get_attr(element, "align")
        layout = self._get_attr(element, "layout")
        original_height = self._get_attr(element, "original-height")
        original_width = self._get_attr(element, "original-width")
        custom_width = self._get_attr(element, "custom-width")

        filename = None
        version_at_save = None
        url_value = None
        children = []

        for child in element:
            child_tag = self._get_tag_name(child)

            if child_tag == "attachment":
                filename = self._get_attr(child, "filename")
                version_at_save = self._get_attr(child, "version-at-save")
            elif child_tag == "url":
                url_value = self._get_attr(child, "value")
            elif child_tag == "caption":
                children = self._parse_children(child)

        return Image(
            src=src,
            alt=alt,
            title=title,
            width=width,
            height=height,
            alignment=alignment,
            layout=layout,
            original_height=original_height,
            original_width=original_width,
            custom_width=custom_width == "true" if custom_width else None,
            filename=filename,
            version_at_save=version_at_save,
            url_value=url_value,
            children=children,
        )

    def _parse_emoticon(self, element: ET.Element) -> Emoticon:
        """Parse ac:emoticon elements."""
        name = self._get_attr(element, "name")
        emoji_shortname = self._get_attr(element, "emoji-shortname")
        emoji_id = self._get_attr(element, "emoji-id")
        emoji_fallback = self._get_attr(element, "emoji-fallback")

        return Emoticon(
            name=name or "", emoji_shortname=emoji_shortname, emoji_id=emoji_id, emoji_fallback=emoji_fallback
        )

    def _parse_placeholder(self, element: ET.Element) -> PlaceholderElement:
        """Parse placeholder elements."""
        text = self._extract_text_content(element)
        return PlaceholderElement(text=text)

    def _parse_time(self, element: ET.Element) -> Time:
        """Parse time elements."""
        datetime = self._get_attr(element, "datetime")
        return Time(datetime=datetime)

    def _parse_resource_identifier(self, element: ET.Element) -> ResourceIdentifier:
        """Parse ri:* resource identifier elements."""
        tag = self._get_tag_name(element)
        resource_type = ResourceIdentifierType(tag)

        space_key = self._get_attr(element, "space-key")
        content_title = self._get_attr(element, "content-title")
        content_id = self._get_attr(element, "content-id")

        posting_day = self._get_attr(element, "posting-day")
        filename = self._get_attr(element, "filename")
        value = self._get_attr(element, "value")
        key = self._get_attr(element, "key")
        parameter = self._get_attr(element, "parameter")
        account_id = self._get_attr(element, "account-id")
        local_id = self._get_attr(element, "local-id")
        userkey = self._get_attr(element, "userkey")
        version_at_save = self._get_attr(element, "version-at-save")

        return ResourceIdentifier(
            type=resource_type,
            space_key=space_key,
            content_title=content_title,
            content_id=content_id,
            posting_day=posting_day,
            filename=filename,
            value=value,
            key=key,
            parameter=parameter,
            account_id=account_id,
            local_id=local_id,
            userkey=userkey,
            version_at_save=version_at_save,
        )

    def _parse_table(self, element: ET.Element) -> Table:
        """Parse table elements."""
        width = self._get_attr(element, "data-table-width")
        layout = self._get_attr(element, "data-layout")
        local_id = self._get_attr(element, "local-id")
        display_mode = self._get_attr(element, "data-table-display-mode")

        return Table(
            width=width,
            layout=layout,
            local_id=local_id,
            display_mode=display_mode,
            children=self._parse_children(element),
        )

    def _parse_table_body(self, element: ET.Element) -> Fragment:
        """Parse tbody elements as fragment containers."""
        return Fragment(children=self._parse_children(element))

    def _parse_table_row(self, element: ET.Element) -> TableRow:
        """Parse tr elements."""
        return TableRow(children=self._parse_children(element))

    def _parse_table_cell(self, element: ET.Element) -> TableCell:
        """Parse th/td elements."""
        tag = self._get_tag_name(element)
        rowspan = self._get_attr(element, "rowspan")
        colspan = self._get_attr(element, "colspan")
        styles = self._parse_css_styles(element)

        return TableCell(
            is_header=tag == "th",
            rowspan=int(rowspan) if rowspan else None,
            colspan=int(colspan) if colspan else None,
            styles=styles,
            children=self._parse_children(element),
        )

    def _parse_macro(self, element: ET.Element) -> Node | None:
        """Parse simple macros by dispatching to specific handlers."""
        name = self._get_attr(element, "name") or ""
        parser = self._macro_parsers.get(name)

        if parser:
            return parser(element)

        self.diagnostics.append(f"unknown_macro:{name}")
        return None

    def _parse_structured_macro(self, element: ET.Element) -> Node | None:
        """Parse structured macros by dispatching to specific handlers."""
        name = self._get_attr(element, "name") or ""
        parser = self._macro_parsers.get(name)

        if parser:
            return parser(element)

        self.diagnostics.append(f"unknown_macro:{name}")
        return None

    def _parse_adf_extension(self, element: ET.Element) -> Node | None:
        """Parse ADF extension elements that can contain various types of content."""
        adf_node = self._find_child_by_tag(element, "adf-node")
        if adf_node is None:
            return None

        node_type = self._get_attr(adf_node, "type")

        if node_type == "panel":
            return self._parse_adf_panel(adf_node)
        elif node_type == "decision-list":
            return self._parse_adf_decision_list(adf_node)
        elif node_type == "decision-item":
            return self._parse_adf_decision_item(adf_node)

        self.diagnostics.append(f"unknown_adf_node_type:{node_type}")
        return None

    def _parse_adf_panel(self, adf_node: ET.Element) -> PanelMacro:
        """Parse ADF panel node into PanelMacro."""
        panel_type_name = "panel"
        bg_color = None

        for attr_elem in adf_node:
            if self._get_tag_name(attr_elem) == "adf-attribute":
                key = self._get_attr(attr_elem, "key")
                value = self._extract_text_content(attr_elem)

                if key == "panel-type":
                    panel_type_name = value
                elif key == "bg-color" or key == "bgColor":
                    bg_color = value

        if panel_type_name == "note":
            panel_type = PanelMacroType.NOTE
        else:
            panel_type = PanelMacroType.PANEL

        children = []
        adf_content = self._find_child_by_tag(adf_node, "adf-content")
        if adf_content is not None:
            children = self._parse_children(adf_content)

        return PanelMacro(
            type=panel_type,
            bg_color=bg_color,
            panel_icon=None,
            panel_icon_id=None,
            panel_icon_text=None,
            children=children,
        )

    def _parse_adf_decision_list(self, adf_node: ET.Element) -> DecisionList:
        """Parse ADF decision-list node into DecisionList."""
        local_id = None

        for attr_elem in adf_node:
            if self._get_tag_name(attr_elem) == "adf-attribute":
                key = self._get_attr(attr_elem, "key")
                value = self._extract_text_content(attr_elem)

                if key == "local-id":
                    local_id = value

        children = []
        for child in adf_node:
            if self._get_tag_name(child) == "adf-node":
                decision_item = self._parse_adf_decision_item(child)
                if decision_item:
                    children.append(decision_item)

        return DecisionList(local_id=local_id, children=children)

    def _parse_adf_decision_item(self, adf_node: ET.Element) -> DecisionListItem:
        """Parse ADF decision-item node into DecisionListItem."""
        local_id = None
        state = None

        for attr_elem in adf_node:
            if self._get_tag_name(attr_elem) == "adf-attribute":
                key = self._get_attr(attr_elem, "key")
                value = self._extract_text_content(attr_elem)

                if key == "local-id":
                    local_id = value
                elif key == "state":
                    if value in ["DECIDED", "PENDING"]:
                        state = DecisionListItemState(value)

        children = []
        adf_content = self._find_child_by_tag(adf_node, "adf-content")
        if adf_content is not None:
            children = self._parse_children(adf_content)

        return DecisionListItem(local_id=local_id, state=state, children=children)

    def _parse_panel_macro(self, element: ET.Element) -> PanelMacro:
        """Parse panel macro elements (panel, tip, note, warning, info)."""
        name = self._get_attr(element, "name") or ""

        if name == "tip":
            panel_type = PanelMacroType.SUCCESS
        elif name == "note":
            panel_type = PanelMacroType.WARNING
        elif name == "warning":
            panel_type = PanelMacroType.ERROR
        elif name == "info":
            panel_type = PanelMacroType.INFO
        else:
            panel_type = PanelMacroType.PANEL

        bg_color = None
        panel_icon = None
        panel_icon_id = None
        panel_icon_text = None

        for param in self._iter_parameters(element):
            param_name = self._get_attr(param, "name")
            param_value = self._extract_text_content(param)

            if param_name == "bgColor":
                bg_color = param_value
            elif param_name == "panelIcon":
                panel_icon = param_value
            elif param_name == "panelIconId":
                panel_icon_id = param_value
            elif param_name == "panelIconText":
                panel_icon_text = param_value

        children = []
        rich_text_body = self._find_child_by_tag(element, "rich-text-body")
        if rich_text_body is not None:
            children = self._parse_children(rich_text_body)

        return PanelMacro(
            type=panel_type,
            bg_color=bg_color,
            panel_icon=panel_icon,
            panel_icon_id=panel_icon_id,
            panel_icon_text=panel_icon_text,
            children=children,
        )

    def _parse_code_macro(self, element: ET.Element) -> CodeMacro:
        """Parse code macro elements."""
        language = None
        breakout_mode = None
        breakout_width = None

        for param in self._iter_parameters(element):
            param_name = self._get_attr(param, "name")
            param_value = self._extract_text_content(param)

            if param_name == "language":
                language = param_value
            elif param_name == "breakoutMode":
                breakout_mode = param_value
            elif param_name == "breakoutWidth":
                breakout_width = param_value

        code = ""
        plain_text_body = self._find_child_by_tag(element, "plain-text-body")
        if plain_text_body is not None:
            code = self._extract_text_content(plain_text_body)

        return CodeMacro(language=language, breakout_mode=breakout_mode, breakout_width=breakout_width, code=code)

    def _parse_details_macro(self, element: ET.Element) -> DetailsMacro:
        """Parse details macro elements."""
        children = []
        rich_text_body = self._find_child_by_tag(element, "rich-text-body")
        if rich_text_body is not None:
            children = self._parse_children(rich_text_body)

        return DetailsMacro(children=children)

    def _parse_expand_macro(self, element: ET.Element) -> ExpandMacro:
        """Parse expand macro elements."""
        title = None
        breakout_width = None

        for param in self._iter_parameters(element):
            param_name = self._get_attr(param, "name")
            param_value = self._extract_text_content(param)

            if param_name == "title":
                title = param_value
            elif param_name == "breakoutWidth":
                breakout_width = param_value

        children = []
        rich_text_body = self._find_child_by_tag(element, "rich-text-body")
        if rich_text_body is not None:
            children = self._parse_children(rich_text_body)

        return ExpandMacro(title=title, breakout_width=breakout_width, children=children)

    def _parse_status_macro(self, element: ET.Element) -> StatusMacro:
        """Parse status macro elements."""
        title = None
        colour = None

        for param in self._iter_parameters(element):
            param_name = self._get_attr(param, "name")
            param_value = self._extract_text_content(param)

            if param_name == "title":
                title = param_value
            elif param_name == "colour":
                colour = param_value

        return StatusMacro(title=title, colour=colour)

    def _parse_toc_macro(self, element: ET.Element) -> TocMacro:
        """Parse table of contents macro elements."""
        style = None

        for param in self._iter_parameters(element):
            param_name = self._get_attr(param, "name")
            param_value = self._extract_text_content(param)

            if param_name == "style":
                style = param_value

        return TocMacro(style=style)

    def _parse_jira_macro(self, element: ET.Element) -> JiraMacro:
        """Parse JIRA macro elements."""
        key = None
        server_id = None
        server = None

        for param in self._iter_parameters(element):
            param_name = self._get_attr(param, "name")
            param_value = self._extract_text_content(param)

            if param_name == "key":
                key = param_value
            elif param_name == "serverId":
                server_id = param_value
            elif param_name == "server":
                server = param_value

        return JiraMacro(key=key, server_id=server_id, server=server)

    def _parse_include_macro(self, element: ET.Element) -> IncludeMacro:
        """Parse include macro elements."""
        children = []
        space_key = None
        content_title = None
        version_at_save = None

        for param in self._iter_parameters(element):
            param_name = self._get_attr(param, "name")
            if param_name == "":
                children = self._parse_children(param)
                for child in children:
                    if hasattr(child, "space_key"):
                        space_key = child.space_key
                    if hasattr(child, "content_title"):
                        content_title = child.content_title
                    if hasattr(child, "version_at_save"):
                        version_at_save = child.version_at_save

        return IncludeMacro(
            space_key=space_key, content_title=content_title, version_at_save=version_at_save, children=children
        )

    def _parse_tasks_report_macro(self, element: ET.Element) -> TasksReportMacro:
        """Parse tasks-report-macro elements."""
        spaces = None
        is_missing_required_parameters = False

        for param in self._iter_parameters(element):
            param_name = self._get_attr(param, "name")
            param_value = self._extract_text_content(param)

            if param_name == "spaces":
                spaces = param_value
            elif param_name == "isMissingRequiredParameters":
                is_missing_required_parameters = param_value.lower() == "true"

        return TasksReportMacro(spaces=spaces, is_missing_required_parameters=is_missing_required_parameters)

    def _parse_excerpt_include_macro(self, element: ET.Element) -> ExcerptIncludeMacro:
        """Parse excerpt-include macro elements."""
        children = []
        space_key = None
        content_title = None
        posting_day = None
        version_at_save = None

        for param in self._iter_parameters(element):
            param_name = self._get_attr(param, "name")
            if param_name == "":
                children = self._parse_children(param)
                for child in children:
                    if hasattr(child, "space_key"):
                        space_key = child.space_key
                    if hasattr(child, "content_title"):
                        content_title = child.content_title
                    if hasattr(child, "posting_day"):
                        posting_day = child.posting_day
                    if hasattr(child, "version_at_save"):
                        version_at_save = child.version_at_save

        return ExcerptIncludeMacro(
            space_key=space_key,
            content_title=content_title,
            posting_day=posting_day,
            version_at_save=version_at_save,
            children=children,
        )

    def _parse_attachments_macro(self, element: ET.Element) -> AttachmentsMacro:
        """Parse attachments macro elements."""
        return AttachmentsMacro()

    def _parse_viewpdf_macro(self, element: ET.Element) -> ViewPdfMacro:
        """Parse viewpdf macro elements."""
        filename = None
        version_at_save = None

        for param in self._iter_parameters(element):
            param_name = self._get_attr(param, "name")
            if param_name == "name":
                for child in param:
                    if self._get_tag_name(child) == "attachment":
                        filename = self._get_attr(child, "filename")
                        version_at_save = self._get_attr(child, "version-at-save")

        return ViewPdfMacro(filename=filename, version_at_save=version_at_save)

    def _parse_view_file_macro(self, element: ET.Element) -> ViewFileMacro:
        """Parse view-file macro elements."""
        filename = None
        version_at_save = None

        for param in self._iter_parameters(element):
            param_name = self._get_attr(param, "name")
            if param_name == "name":
                for child in param:
                    if self._get_tag_name(child) == "attachment":
                        filename = self._get_attr(child, "filename")
                        version_at_save = self._get_attr(child, "version-at-save")

        return ViewFileMacro(filename=filename, version_at_save=version_at_save)

    def _parse_profile_macro(self, element: ET.Element) -> ProfileMacro:
        """Parse profile macro elements."""
        children = []
        account_id = None

        for param in self._iter_parameters(element):
            param_name = self._get_attr(param, "name")
            if param_name == "user":
                children = self._parse_children(param)
                for child in children:
                    if hasattr(child, "account_id"):
                        account_id = child.account_id

        return ProfileMacro(account_id=account_id, children=children)

    def _parse_anchor_macro(self, element: ET.Element) -> AnchorMacro:
        """Parse anchor macro elements."""
        anchor_name = None

        for param in self._iter_parameters(element):
            param_name = self._get_attr(param, "name")
            param_value = self._extract_text_content(param)

            if param_name == "":
                anchor_name = param_value

        return AnchorMacro(anchor_name=anchor_name)

    def _parse_excerpt_macro(self, element: ET.Element) -> ExcerptMacro:
        """Parse excerpt macro elements."""
        children = []
        rich_text_body = self._find_child_by_tag(element, "rich-text-body")
        if rich_text_body is not None:
            children = self._parse_children(rich_text_body)

        return ExcerptMacro(children=children)

    def _get_tag_name(self, element: ET.Element) -> str:
        """Extract tag name without namespace prefix."""
        tag = element.tag
        return tag.split("}", 1)[1] if "}" in tag else tag

    def _get_attr(self, element: ET.Element, attr_name: str) -> str | None:
        """Get attribute value handling multiple namespace variants."""
        value = element.attrib.get(attr_name)
        if value is not None:
            return value

        for ns in [self.NS_AC, self.NS_RI, self.NS_AT]:
            value = element.attrib.get(f"{{{ns}}}{attr_name}")
            if value is not None:
                return value

        return None

    def _find_child_by_tag(self, element: ET.Element, tag_name: str) -> ET.Element | None:
        """Find first direct child with given tag name."""
        for child in element:
            if self._get_tag_name(child) == tag_name:
                return child
        return None

    def _extract_text_content(self, element: ET.Element) -> str:
        """Extract all text content from element and descendants."""
        parts: list[str] = []

        if element.text:
            parts.append(element.text)

        for child in element:
            parts.append(self._extract_text_content(child))
            if child.tail:
                parts.append(child.tail)

        return "".join(parts)

    def _iter_parameters(self, element: ET.Element) -> Iterator[ET.Element]:
        """Iterate over parameter children of a macro element."""
        for child in element:
            if self._get_tag_name(child) == "parameter":
                yield child

    def _parse_css_styles(self, element: ET.Element) -> dict[str, str]:
        """Parse all CSS styles from element's style attribute."""
        style_attr = self._get_attr(element, "style") or ""
        styles = {}

        for declaration in style_attr.split(";"):
            if ":" in declaration:
                prop, value = declaration.split(":", 1)
                prop = prop.strip().lower()
                value = value.strip()

                if prop and value:
                    styles[prop] = value

        return styles
