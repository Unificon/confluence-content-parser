from __future__ import annotations

from lxml import etree
from lxml.etree import QName, XMLParser, _Element

from .models import (
    AdfExtension,
    AdfFallback,
    AdfNode,
    AnchorMacro,
    AttachmentReference,
    AttachmentsMacro,
    BlogPostReference,
    ChildrenDisplayMacro,
    CodeBlock,
    ConfluenceDocument,
    ContentElement,
    ContentEntityReference,
    DateElement,
    DecisionItem,
    DecisionList,
    Emoticon,
    ExcerptIncludeMacro,
    ExcerptMacro,
    ExpandMacro,
    GadgetMacro,
    I18nElement,
    Image,
    InlineComment,
    JiraMacro,
    LayoutCell,
    LayoutSection,
    Link,
    NotificationMacro,
    PagePropertiesMacro,
    PagePropertiesReportMacro,
    PageReference,
    Panel,
    Placeholder,
    ShortcutReference,
    SpaceReference,
    Status,
    StructuredMacro,
    Table,
    Task,
    TaskElement,
    TaskItem,
    TaskList,
    TaskListContainer,
    TocMacro,
    UrlReference,
    UserReference,
    ViewFileMacro,
)


class ConfluenceParser:
    NAMESPACES = {
        "ac": "http://www.atlassian.com/schema/confluence/4/ac/",
        "ri": "http://www.atlassian.com/schema/confluence/4/ri/",
        "at": "http://www.atlassian.com/schema/confluence/4/at/",
    }

    def __init__(self) -> None:
        self.xml_parser = XMLParser(ns_clean=True, remove_blank_text=True, recover=True, resolve_entities=True)
        self.diagnostics: list[str] = []

    def parse(self, content: str) -> ConfluenceDocument:
        self.diagnostics = []
        root = self._parse_xml(content)
        doc_content: list[ContentElement] = []

        if root.tag == "root" and len(root) > 0:
            for child in root:
                self._parse_element(child, doc_content)
        else:
            self._parse_element(root, doc_content)

        self._annotate_elements(doc_content)
        return ConfluenceDocument(content=doc_content, metadata={"diagnostics": self.diagnostics})

    def _parse_xml(self, content: str) -> _Element:
        if self._needs_namespace_wrapping(content):
            content = self._wrap_with_namespaces(content)
        return etree.fromstring(content.encode("utf-8"), self.xml_parser)

    def _needs_namespace_wrapping(self, content: str) -> bool:
        return "xmlns:ac=" not in content and ("ac:" in content or "ri:" in content or "at:" in content)

    def _wrap_with_namespaces(self, content: str) -> str:
        namespace_declarations = " ".join(f'xmlns:{prefix}="{uri}"' for prefix, uri in self.NAMESPACES.items())
        return f"""<?xml version="1.0" encoding="UTF-8"?>
                   <root {namespace_declarations}>
                       {content}
                   </root>"""

    def _parse_element(self, element: _Element, content_list: list[ContentElement]) -> None:
        tag = self._get_local_name(element.tag)

        match tag:
            case "layout" | "ac:layout":
                self._parse_layout(element, content_list)
            case "layout-section" | "ac:layout-section":
                self._parse_layout_section(element, content_list)
            case "layout-cell" | "ac:layout-cell":
                self._parse_layout_cell(element, content_list)
            case "structured-macro" | "ac:structured-macro":
                self._parse_structured_macro(element, content_list)
            case "link" | "ac:link":
                self._parse_link(element, content_list)
            case "inline-comment-marker" | "ac:inline-comment-marker":
                self._parse_inline_comment(element, content_list)
            case "emoticon" | "ac:emoticon":
                self._parse_emoticon(element, content_list)
            case "placeholder" | "ac:placeholder":
                self._parse_placeholder(element, content_list)
            case "image" | "ac:image":
                self._parse_image(element, content_list)
            case "task" | "ac:task":
                self._parse_task(element, content_list)
            case "i18n" | "at:i18n":
                self._parse_i18n(element, content_list)
            case "adf-extension" | "ac:adf-extension":
                self._parse_adf_extension(element, content_list)
            case "task-list" | "ac:task-list":
                self._parse_task_list_container(element, content_list)
            case "adf-node" | "ac:adf-node":
                self._parse_adf_node(element, content_list)
            case "adf-fallback" | "ac:adf-fallback":
                self._parse_adf_fallback(element, content_list)
            case "hr":
                self._parse_horizontal_rule(element, content_list)
            case "table":
                self._parse_table(element, content_list)
            case "time":
                self._parse_date(element, content_list)
            case "a":
                self._parse_anchor_link(element, content_list)
            case _:
                if self._is_text_element(tag):
                    self._parse_text_element(element, content_list, tag)
                else:
                    self._parse_generic_element(element, content_list, tag)

    def _is_text_element(self, tag: str) -> bool:
        return tag in {
            "p",
            "div",
            "span",
            "strong",
            "em",
            "h1",
            "h2",
            "h3",
            "h4",
            "h5",
            "h6",
            "blockquote",
            "ul",
            "ol",
            "li",
            "hr",
            "br",
            "pre",
            "code",
            "u",
            "del",
            "sub",
            "sup",
            "s",
            "mark",
        }

    def _get_local_name(self, tag: str | bytes | bytearray | QName) -> str:
        tag_str = str(tag)
        return tag_str.split("}", 1)[1] if "}" in tag_str else tag_str

    def _get_attribute(self, element: _Element, attr_name: str) -> str | None:
        for prefix, namespace in self.NAMESPACES.items():
            for attr_variant in [f"{{{namespace}}}{attr_name}", f"{prefix}:{attr_name}", attr_name]:
                value = element.get(attr_variant)
                if value is not None:
                    return value
        return None

    def _parse_layout(self, element: _Element, content_list: list[ContentElement]) -> None:
        children: list[ContentElement] = []
        for child in element:
            self._parse_element(child, children)

        content_list.append(ContentElement(type="layout", children=children, attributes=dict(element.attrib)))

    def _parse_layout_section(self, element: _Element, content_list: list[ContentElement]) -> None:
        layout_section = LayoutSection(
            type=self._get_attribute(element, "type") or "",
            breakout_mode=self._get_attribute(element, "breakout-mode"),
            breakout_width=self._get_attribute(element, "breakout-width"),
        )

        for child in element:
            if self._get_local_name(child.tag) in ("layout-cell", "ac:layout-cell"):
                cell_content: list[ContentElement] = []
                for cell_child in child:
                    self._parse_element(cell_child, cell_content)
                layout_section.cells.append(LayoutCell(content=cell_content))

        content_list.append(
            ContentElement(type="layout_section", layout_section=layout_section, attributes=dict(element.attrib))
        )

    def _parse_layout_cell(self, element: _Element, content_list: list[ContentElement]) -> None:
        children: list[ContentElement] = []
        for child in element:
            self._parse_element(child, children)

        content_list.append(
            ContentElement(
                type="layout_cell", layout_cell=LayoutCell(content=children), attributes=dict(element.attrib)
            )
        )

    def _parse_structured_macro(self, element: _Element, content_list: list[ContentElement]) -> None:
        macro = self._build_structured_macro(element)

        if macro.name == "status":
            self._handle_status_macro(macro, element, content_list)
        elif macro.name == "code":
            self._handle_code_macro(macro, element, content_list)
        elif macro.name == "jira":
            self._handle_jira_macro(macro, element, content_list)
        elif macro.name == "task-list":
            self._handle_task_list_macro(macro, element, content_list)
        elif macro.name == "panel":
            self._handle_panel_macro(macro, element, content_list)
        elif macro.name in ("info", "warning", "note", "tip"):
            self._handle_notification_macro(macro, element, content_list)
        elif macro.name == "view-file":
            self._handle_view_file_macro(macro, element, content_list)
        elif macro.name == "gadget":
            self._handle_gadget_macro(macro, element, content_list)
        elif macro.name == "expand":
            self._handle_expand_macro(macro, element, content_list)
        elif macro.name == "toc":
            self._handle_toc_macro(macro, element, content_list)
        elif macro.name == "anchor":
            self._handle_anchor_macro(macro, element, content_list)
        elif macro.name == "excerpt":
            self._handle_excerpt_macro(macro, element, content_list)
        elif macro.name == "excerpt-include":
            self._handle_excerpt_include_macro(macro, element, content_list)
        elif macro.name == "page-properties":
            self._handle_page_properties_macro(macro, element, content_list)
        elif macro.name == "page-properties-report":
            self._handle_page_properties_report_macro(macro, element, content_list)
        elif macro.name == "children-display":
            self._handle_children_display_macro(macro, element, content_list)
        elif macro.name == "attachments":
            self._handle_attachments_macro(macro, element, content_list)
        else:
            self.diagnostics.append(f"unknown_macro:{macro.name}")
            content_list.append(ContentElement(type="macro", macro=macro, attributes=dict(element.attrib)))

    def _build_structured_macro(self, element: _Element) -> StructuredMacro:
        name = self._get_attribute(element, "name") or ""
        macro_id = self._get_attribute(element, "macro-id") or ""
        schema_version = self._get_attribute(element, "schema-version")

        macro = StructuredMacro(
            name=name,
            macro_id=macro_id,
            schema_version=schema_version,
            layout=element.get("data-layout"),
        )

        for child in element:
            child_tag = self._get_local_name(child.tag)

            if child_tag in ("parameter", "ac:parameter"):
                param_name = self._get_attribute(child, "name") or ""
                attachment = child.find(".//{*}attachment")
                if attachment is not None:
                    filename = self._get_attribute(attachment, "filename")
                    version_at_save = self._get_attribute(attachment, "version-at-save")
                    macro.parameters[param_name] = child.text or filename or ""
                    if filename:
                        macro.parameters[f"{param_name}__attachment_filename"] = filename
                    if version_at_save:
                        macro.parameters[f"{param_name}__attachment_version_at_save"] = version_at_save
                else:
                    macro.parameters[param_name] = child.text or ""
            elif child_tag in ("plain-text-body", "ac:plain-text-body"):
                macro.body = child.text
            elif child_tag in ("rich-text-body", "ac:rich-text-body"):
                macro.body = self._extract_text(child)

        return macro

    def _handle_status_macro(
        self, macro: StructuredMacro, element: _Element, content_list: list[ContentElement]
    ) -> None:
        status = Status(
            title=macro.parameters.get("title", ""),
            colour=macro.parameters.get("colour", ""),
        )
        content_list.append(ContentElement(type="status", status=status, attributes=dict(element.attrib)))

    def _handle_code_macro(self, macro: StructuredMacro, element: _Element, content_list: list[ContentElement]) -> None:
        code_block = CodeBlock(
            language=macro.parameters.get("language"),
            title=macro.parameters.get("title"),
            collapse=macro.parameters.get("collapse") == "true",
            linenumbers=macro.parameters.get("linenumbers") == "true",
            theme=macro.parameters.get("theme"),
            breakout_mode=macro.parameters.get("breakoutMode"),
            breakout_width=macro.parameters.get("breakoutWidth"),
            content=macro.body or "",
        )
        content_list.append(ContentElement(type="code_block", code_block=code_block, attributes=dict(element.attrib)))

    def _handle_jira_macro(self, macro: StructuredMacro, element: _Element, content_list: list[ContentElement]) -> None:
        jira_macro = JiraMacro(
            key=macro.parameters.get("key", ""),
            server_id=macro.parameters.get("serverId", ""),
            server=macro.parameters.get("server", ""),
        )
        content_list.append(ContentElement(type="jira_macro", jira_macro=jira_macro, attributes=dict(element.attrib)))

    def _handle_task_list_macro(
        self, macro: StructuredMacro, element: _Element, content_list: list[ContentElement]
    ) -> None:
        task_list = TaskList(local_id=macro.macro_id)

        for child in element:
            if self._get_local_name(child.tag) in ("task-item", "ac:task-item"):
                task_item = TaskItem(
                    local_id=self._get_attribute(child, "local-id") or "",
                    task_id=self._get_attribute(child, "task-id") or "",
                    completed=self._get_attribute(child, "completed") == "true",
                    content=self._extract_text(child),
                )
                task_list.items.append(task_item)

        content_list.append(ContentElement(type="task_list", task_list=task_list, attributes=dict(element.attrib)))

    def _parse_link(self, element: _Element, content_list: list[ContentElement]) -> None:
        link = Link(
            card_appearance=element.get("data-card-appearance"),
            anchor=self._get_attribute(element, "anchor"),
        )

        for child in element:
            self._process_link_child(child, link)

        content_list.append(ContentElement(type="link", link=link, attributes=dict(element.attrib)))

    def _process_link_child(self, child: _Element, link: Link) -> None:
        child_tag = self._get_local_name(child.tag)

        match child_tag:
            case "user" | "ri:user":
                link.user_reference = UserReference(
                    account_id=self._get_attribute(child, "account-id") or "",
                    local_id=self._get_attribute(child, "local-id"),
                )
            case "page" | "ri:page":
                link.page_reference = PageReference(
                    content_title=self._get_attribute(child, "content-title") or "",
                    space_key=self._get_attribute(child, "space-key"),
                    version_at_save=self._get_attribute(child, "version-at-save"),
                )
            case "attachment" | "ri:attachment":
                link.attachment_reference = AttachmentReference(
                    filename=self._get_attribute(child, "filename") or "",
                    content_id=self._get_attribute(child, "content-id"),
                    version_at_save=self._get_attribute(child, "version-at-save"),
                )
            case "url" | "ri:url":
                link.url_reference = UrlReference(
                    value=self._get_attribute(child, "value") or "",
                )
            case "blog-post" | "ri:blog-post":
                link.blog_post_reference = BlogPostReference(
                    content_title=self._get_attribute(child, "content-title") or "",
                    space_key=self._get_attribute(child, "space-key"),
                    posting_day=self._get_attribute(child, "posting-day"),
                )
            case "space" | "ri:space":
                link.space_reference = SpaceReference(space_key=self._get_attribute(child, "space-key") or "")
            case "content-entity" | "ri:content-entity":
                link.content_entity_reference = ContentEntityReference(
                    content_id=self._get_attribute(child, "content-id") or ""
                )
            case "shortcut" | "ri:shortcut":
                link.shortcut_reference = ShortcutReference(
                    key=self._get_attribute(child, "key") or "",
                    parameter=self._get_attribute(child, "parameter") or "",
                )
            case "link-body" | "ac:link-body":
                link.text = child.text or ""
            case "plain-text-link-body" | "ac:plain-text-link-body":
                link.text = child.text or ""
            case _:
                pass

    def _parse_inline_comment(self, element: _Element, content_list: list[ContentElement]) -> None:
        inline_comment = InlineComment(
            ref=self._get_attribute(element, "ref") or "",
            text=element.text or "",
        )

        content_list.append(
            ContentElement(type="inline_comment", inline_comment=inline_comment, attributes=dict(element.attrib))
        )

    def _parse_emoticon(self, element: _Element, content_list: list[ContentElement]) -> None:
        emoticon = Emoticon(
            name=self._get_attribute(element, "name") or "",
            emoji_shortname=self._get_attribute(element, "emoji-shortname"),
            emoji_id=self._get_attribute(element, "emoji-id"),
            emoji_fallback=self._get_attribute(element, "emoji-fallback"),
        )

        content_list.append(ContentElement(type="emoticon", emoticon=emoticon, attributes=dict(element.attrib)))

    def _parse_placeholder(self, element: _Element, content_list: list[ContentElement]) -> None:
        placeholder = Placeholder(
            type=self._get_attribute(element, "type"),
            text=element.text or "",
        )

        content_list.append(
            ContentElement(type="placeholder", placeholder=placeholder, attributes=dict(element.attrib))
        )

    def _parse_image(self, element: _Element, content_list: list[ContentElement]) -> None:
        image = Image(
            alt=self._get_attribute(element, "alt"),
            title=self._get_attribute(element, "title"),
            width=self._get_attribute(element, "width"),
            height=self._get_attribute(element, "height"),
            alignment=self._get_attribute(element, "align"),
            layout=self._get_attribute(element, "layout"),
            original_height=self._get_attribute(element, "original-height"),
            original_width=self._get_attribute(element, "original-width"),
            custom_width=self._get_attribute(element, "custom-width") == "true",
        )

        for child in element:
            self._process_media_child(child, image)

        content_list.append(ContentElement(type="image", image=image, attributes=dict(element.attrib)))

    def _parse_table(self, element: _Element, content_list: list[ContentElement]) -> None:
        table = Table(
            width=element.get("data-table-width"),
            layout=element.get("data-layout"),
            local_id=self._get_attribute(element, "local-id"),
        )

        tbody = element.find(".//tbody")
        if tbody is not None:
            self._process_table_rows(tbody, table)

        content_list.append(ContentElement(type="table", table=table, attributes=dict(element.attrib)))

    def _process_table_rows(self, tbody: _Element, table: Table) -> None:
        for row in tbody.findall(".//tr"):
            cells = row.findall(".//td") + row.findall(".//th")
            rich_row: list[list[ContentElement]] = []
            for cell in cells:
                cell_elements: list[ContentElement] = []
                for child in cell:
                    self._parse_element(child, cell_elements)
                if not cell_elements:
                    cell_elements.append(ContentElement(type="text", text=self._extract_text(cell)))
                rich_row.append(cell_elements)
            table.cells.append(rich_row)

    def _parse_date(self, element: _Element, content_list: list[ContentElement]) -> None:
        date = DateElement(datetime=element.get("datetime", ""))
        content_list.append(ContentElement(type="date", date=date, attributes=dict(element.attrib)))

    def _parse_anchor_link(self, element: _Element, content_list: list[ContentElement]) -> None:
        link = Link(
            url=element.get("href"),
            text=self._extract_text(element),
            card_appearance=element.get("data-card-appearance"),
        )

        content_list.append(ContentElement(type="link", link=link, attributes=dict(element.attrib)))

    def _parse_text_element(self, element: _Element, content_list: list[ContentElement], tag: str) -> None:
        children: list[ContentElement] = []
        text_content = element.text or ""

        for child in element:
            self._parse_element(child, children)
            if child.tail:
                children.append(
                    ContentElement(
                        type="text",
                        text=child.tail,
                    )
                )

        content_list.append(
            ContentElement(
                type=tag,
                text=text_content.strip() if text_content.strip() else None,
                children=children,
                attributes=dict(element.attrib),
            )
        )

    def _parse_generic_element(self, element: _Element, content_list: list[ContentElement], tag: str) -> None:
        children: list[ContentElement] = []
        for child in element:
            self._parse_element(child, children)

        content_list.append(
            ContentElement(type=tag, text=element.text, children=children, attributes=dict(element.attrib))
        )

    def _extract_text(self, element: _Element) -> str:
        return "".join(element.itertext()).strip()

    def _annotate_elements(self, elements: list[ContentElement]) -> None:
        def walk(
            el: ContentElement,
            path: list[str | int],
            idx: int,
            heading_stack: list[str],
            list_stack: list[str],
            layout_ctx: dict[str, str | int | None] | None,
        ) -> None:
            el.path = path.copy()
            el.sibling_index = idx
            el.id = self._assign_id(el, path)
            el.heading_scope_id = heading_stack[-1] if heading_stack else None
            el.list_scope = {"type": list_stack[-1], "depth": len(list_stack)} if list_stack else {}
            el.layout_scope = layout_ctx or {}
            if el.type in {"h1", "h2", "h3", "h4", "h5", "h6"}:
                heading_stack.append(el.id or "")
            pushed_list = False
            if el.type in {"ul", "ol"}:
                list_stack.append(el.type)
                pushed_list = True
            for i, child in enumerate(el.children):
                walk(child, path + ["children", i], i, heading_stack, list_stack, layout_ctx)
            if el.layout_section is not None and hasattr(el, "layout_section"):
                sec = el.layout_section
                for ci, cell in enumerate(sec.cells):
                    cell_ctx = {
                        "section_type": getattr(sec, "type", None),
                        "section_index": (el.sibling_index or 0),
                        "cell_index": ci,
                        "breakout_mode": getattr(sec, "breakout_mode", None),
                        "breakout_width": getattr(sec, "breakout_width", None),
                    }
                    for k, cell_el in enumerate(cell.content):
                        walk(cell_el, path + ["cells", ci, "content", k], k, heading_stack, list_stack, cell_ctx)
            if el.type in {"h1", "h2", "h3", "h4", "h5", "h6"} and heading_stack:
                heading_stack.pop()
            if pushed_list and list_stack:
                list_stack.pop()

        for i, el in enumerate(elements):
            walk(el, ["content", i], i, [], [], {})

    def _compute_element_id(self, path: list[str | int]) -> str:
        data = "/".join(str(p) for p in path)
        return f"el:{abs(hash(data))}"

    def _assign_id(self, el: ContentElement, path: list[str | int]) -> str:
        if el.link and el.link.kind == "page" and el.link.page_reference:
            ct = el.link.page_reference.content_title
            sk = el.link.page_reference.space_key or ""
            return f"page://{sk}/{ct}"
        if el.link and el.link.kind == "content_entity" and el.link.content_entity_reference:
            return f"contentid://{el.link.content_entity_reference.content_id}"
        if el.link and el.link.kind == "user" and el.link.user_reference:
            if el.link.user_reference.account_id:
                return f"user://{el.link.user_reference.account_id}"
        if el.link and el.link.kind == "attachment" and el.link.attachment_reference:
            ar = el.link.attachment_reference
            ver = f"@v{ar.version_at_save}" if ar.version_at_save is not None else ""
            return f"attach://{ar.filename}{ver}"
        return self._compute_element_id(path)

    def _parse_task(self, element: _Element, content_list: list[ContentElement]) -> None:
        task = Task(
            local_id=self._get_attribute(element, "local-id") or "",
            task_id=self._get_attribute(element, "task-id") or "",
            status=self._get_attribute(element, "status") or "incomplete",
            body=self._extract_text(element),
        )

        content_list.append(ContentElement(type="task", task=task, attributes=dict(element.attrib)))

    def _parse_i18n(self, element: _Element, content_list: list[ContentElement]) -> None:
        i18n = I18nElement(
            key=self._get_attribute(element, "key") or "",
        )

        content_list.append(ContentElement(type="i18n", i18n=i18n, attributes=dict(element.attrib)))

    def _parse_adf_extension(self, element: _Element, content_list: list[ContentElement]) -> None:
        parameters: dict[str, str] = {}
        content = ""
        nested_nodes: list[ContentElement] = []
        decision_node_detected = False
        decision_local_id: str | None = None

        for child in element:
            child_tag = self._get_local_name(child.tag)
            if child_tag in ("parameter", "ac:parameter"):
                param_name = self._get_attribute(child, "name") or ""
                parameters[param_name] = child.text or ""
            elif child_tag in ("content", "ac:content"):
                for grandchild in child:
                    self._parse_element(grandchild, nested_nodes)
                content = self._extract_text(child)
            elif child_tag in ("adf-node", "ac:adf-node"):
                if (self._get_attribute(child, "type") or "") == "decision-list":
                    decision_node_detected = True
                    decision_local_id = self._get_attribute(child, "local-id") or ""
                self._parse_element(child, nested_nodes)
            elif child_tag in ("adf-fallback", "ac:adf-fallback"):
                if decision_node_detected:
                    items: list[DecisionItem] = []
                    for li in child.findall(".//li"):
                        text = self._extract_text(li)
                        if text:
                            items.append(DecisionItem(state="DECIDED", content=text))
                    if items:
                        decision_list = DecisionList(local_id=decision_local_id or "", items=items)
                        content_list.append(
                            ContentElement(type="decision_list", decision_list=decision_list, attributes={})
                        )
                self._parse_element(child, nested_nodes)

        adf_extension = AdfExtension(
            extension_type=self._get_attribute(element, "extension-type"),
            extension_key=self._get_attribute(element, "extension-key"),
            parameters=parameters,
            content=content,
        )

        content_list.append(
            ContentElement(type="adf_extension", adf_extension=adf_extension, attributes=dict(element.attrib))
        )
        content_list.extend(nested_nodes)

    def _handle_panel_macro(
        self, macro: StructuredMacro, element: _Element, content_list: list[ContentElement]
    ) -> None:
        panel_children: list[ContentElement] = []
        for child in element:
            if self._get_local_name(child.tag) in ("rich-text-body", "ac:rich-text-body"):
                for body_child in child:
                    self._parse_element(body_child, panel_children)

        panel = Panel(
            title=macro.parameters.get("title"),
            border_style=macro.parameters.get("borderStyle"),
            border_color=macro.parameters.get("borderColor"),
            title_bg_color=macro.parameters.get("titleBGColor"),
            title_color=macro.parameters.get("titleColor"),
            bg_color=macro.parameters.get("bgColor"),
            content=macro.body or "",
            icon=macro.parameters.get("panelIcon"),
            icon_id=macro.parameters.get("panelIconId"),
            icon_text=macro.parameters.get("panelIconText"),
            children=panel_children,
        )
        content_list.append(ContentElement(type="panel", panel=panel, attributes=dict(element.attrib)))

    def _handle_notification_macro(
        self, macro: StructuredMacro, element: _Element, content_list: list[ContentElement]
    ) -> None:
        notification_macro = NotificationMacro(
            macro_type=macro.name,
            content=macro.body or "",
        )
        content_list.append(
            ContentElement(
                type="notification_macro", notification_macro=notification_macro, attributes=dict(element.attrib)
            )
        )

    def _handle_view_file_macro(
        self, macro: StructuredMacro, element: _Element, content_list: list[ContentElement]
    ) -> None:
        view_file_macro = ViewFileMacro(
            name=macro.parameters.get("name", ""),
            version_at_save=macro.parameters.get("version-at-save"),
            attachment_filename=macro.parameters.get("name__attachment_filename"),
            attachment_version_at_save=macro.parameters.get("name__attachment_version_at_save"),
        )
        content_list.append(
            ContentElement(type="view_file_macro", view_file_macro=view_file_macro, attributes=dict(element.attrib))
        )

    def _handle_gadget_macro(
        self, macro: StructuredMacro, element: _Element, content_list: list[ContentElement]
    ) -> None:
        gadget_macro = GadgetMacro(
            url=macro.parameters.get("url", ""),
            layout=macro.layout,
            local_id=self._get_attribute(element, "local-id"),
        )
        content_list.append(
            ContentElement(type="gadget_macro", gadget_macro=gadget_macro, attributes=dict(element.attrib))
        )

    def _handle_expand_macro(
        self, macro: StructuredMacro, element: _Element, content_list: list[ContentElement]
    ) -> None:
        expand_children: list[ContentElement] = []
        for child in element:
            if self._get_local_name(child.tag) in ("rich-text-body", "ac:rich-text-body"):
                for body_child in child:
                    self._parse_element(body_child, expand_children)

        expand_macro = ExpandMacro(
            title=macro.parameters.get("title", ""),
            breakout_width=macro.parameters.get("breakoutWidth"),
            content=macro.body or "",
            children=expand_children,
        )
        content_list.append(
            ContentElement(type="expand_macro", expand_macro=expand_macro, attributes=dict(element.attrib))
        )

    def _handle_toc_macro(self, macro: StructuredMacro, element: _Element, content_list: list[ContentElement]) -> None:
        toc_macro = TocMacro(
            style=macro.parameters.get("style"),
            local_id=self._get_attribute(element, "local-id"),
        )
        content_list.append(ContentElement(type="toc_macro", toc_macro=toc_macro, attributes=dict(element.attrib)))

    def _handle_anchor_macro(
        self, macro: StructuredMacro, element: _Element, content_list: list[ContentElement]
    ) -> None:
        anchor = AnchorMacro(anchor=macro.parameters.get("anchor", ""))
        content_list.append(ContentElement(type="anchor_macro", anchor_macro=anchor, attributes=dict(element.attrib)))

    def _handle_excerpt_macro(
        self, macro: StructuredMacro, element: _Element, content_list: list[ContentElement]
    ) -> None:
        hidden = macro.parameters.get("hidden") == "true"
        children: list[ContentElement] = []
        for child in element:
            if self._get_local_name(child.tag) in ("rich-text-body", "ac:rich-text-body"):
                for body_child in child:
                    self._parse_element(body_child, children)
        excerpt = ExcerptMacro(
            hidden=hidden,
            atlassian_macro_output_type=element.get("ac:macro-output-type"),
            body=macro.body or "",
            children=children,
        )
        content_list.append(
            ContentElement(type="excerpt_macro", excerpt_macro=excerpt, attributes=dict(element.attrib))
        )

    def _handle_excerpt_include_macro(
        self, macro: StructuredMacro, element: _Element, content_list: list[ContentElement]
    ) -> None:
        include = ExcerptIncludeMacro(page=macro.parameters.get("page", ""))
        content_list.append(
            ContentElement(type="excerpt_include_macro", excerpt_include_macro=include, attributes=dict(element.attrib))
        )

    def _handle_page_properties_macro(
        self, macro: StructuredMacro, element: _Element, content_list: list[ContentElement]
    ) -> None:
        hidden = macro.parameters.get("hidden") == "true"
        children: list[ContentElement] = []
        for child in element:
            if self._get_local_name(child.tag) in ("rich-text-body", "ac:rich-text-body"):
                for body_child in child:
                    self._parse_element(body_child, children)
        ppm = PagePropertiesMacro(
            id=macro.parameters.get("id"), hidden=hidden, body=macro.body or "", children=children
        )
        content_list.append(
            ContentElement(type="page_properties_macro", page_properties_macro=ppm, attributes=dict(element.attrib))
        )

    def _handle_page_properties_report_macro(
        self, macro: StructuredMacro, element: _Element, content_list: list[ContentElement]
    ) -> None:
        labels = [label.strip() for label in (macro.parameters.get("labels", "")).split(",") if label.strip()]
        ppr = PagePropertiesReportMacro(
            id=macro.parameters.get("id"), labels=labels, space_key=macro.parameters.get("spaceKey")
        )
        content_list.append(
            ContentElement(
                type="page_properties_report_macro", page_properties_report_macro=ppr, attributes=dict(element.attrib)
            )
        )

    def _handle_children_display_macro(
        self, macro: StructuredMacro, element: _Element, content_list: list[ContentElement]
    ) -> None:
        cd = ChildrenDisplayMacro(
            depth=int(depth_val) if (depth_val := macro.parameters.get("depth")) else None,
            excerpt=macro.parameters.get("excerpt"),
            sort=macro.parameters.get("sort"),
            reverse=(macro.parameters.get("reverse") == "true") if macro.parameters.get("reverse") else None,
            parent=macro.parameters.get("parent"),
        )
        content_list.append(
            ContentElement(type="children_display_macro", children_display_macro=cd, attributes=dict(element.attrib))
        )

    def _handle_attachments_macro(
        self, macro: StructuredMacro, element: _Element, content_list: list[ContentElement]
    ) -> None:
        patterns = [p.strip() for p in (macro.parameters.get("patterns", "")).split(",") if p.strip()]
        att = AttachmentsMacro(patterns=patterns, page=macro.parameters.get("page"))
        content_list.append(
            ContentElement(type="attachments_macro", attachments_macro=att, attributes=dict(element.attrib))
        )

    def _parse_task_list_container(self, element: _Element, content_list: list[ContentElement]) -> None:
        tasks = []

        for child in element:
            if self._get_local_name(child.tag) in ("task", "ac:task"):
                task_id = ""
                task_uuid = ""
                status = "incomplete"
                body = ""

                for task_child in child:
                    child_tag = self._get_local_name(task_child.tag)
                    if child_tag in ("task-id", "ac:task-id"):
                        task_id = task_child.text or ""
                    elif child_tag in ("task-uuid", "ac:task-uuid"):
                        task_uuid = task_child.text or ""
                    elif child_tag in ("task-status", "ac:task-status"):
                        status = task_child.text or "incomplete"
                    elif child_tag in ("task-body", "ac:task-body"):
                        body = self._extract_text(task_child)

                tasks.append(TaskElement(task_id=task_id, task_uuid=task_uuid, status=status, body=body))

        task_list_container = TaskListContainer(tasks=tasks)
        content_list.append(
            ContentElement(
                type="task_list_container", task_list_container=task_list_container, attributes=dict(element.attrib)
            )
        )

    def _parse_adf_node(self, element: _Element, content_list: list[ContentElement]) -> None:
        node_type = self._get_attribute(element, "type") or ""
        local_id = self._get_attribute(element, "local-id")
        attributes = {}
        content = ""
        children: list[ContentElement] = []

        for child in element:
            child_tag = self._get_local_name(child.tag)
            if child_tag in ("adf-attribute", "ac:adf-attribute"):
                key = self._get_attribute(child, "key") or ""
                attributes[key] = child.text or ""
            elif child_tag in ("adf-content", "ac:adf-content"):
                content = self._extract_text(child)
            elif child_tag in ("adf-node", "ac:adf-node"):
                child_nodes: list[ContentElement] = []
                self._parse_adf_node(child, child_nodes)
                if child_nodes:
                    adf_node = child_nodes[0].adf_node
                    if adf_node and hasattr(adf_node, "children"):
                        children.extend(
                            [
                                ContentElement(type="content", text=str(child), attributes={})
                                for child in adf_node.children
                            ]
                        )

        if node_type == "decision-list":
            decision_items = []
            for li in element.findall(".//li"):
                text = self._extract_text(li)
                if text:
                    decision_items.append(DecisionItem(local_id="", state="DECIDED", content=text))
            decision_list = DecisionList(local_id=self._get_attribute(element, "local-id") or "", items=decision_items)
            content_list.append(
                ContentElement(type="decision_list", decision_list=decision_list, attributes=dict(element.attrib))
            )
            return

        adf_node = AdfNode(type=node_type, local_id=local_id, attributes=attributes, content=content, children=children)
        content_list.append(ContentElement(type="adf_node", adf_node=adf_node, attributes=dict(element.attrib)))

    def _parse_adf_fallback(self, element: _Element, content_list: list[ContentElement]) -> None:
        adf_fallback = AdfFallback(content=self._extract_text(element))
        content_list.append(
            ContentElement(type="adf_fallback", adf_fallback=adf_fallback, attributes=dict(element.attrib))
        )

    def _parse_horizontal_rule(self, element: _Element, content_list: list[ContentElement]) -> None:
        content_list.append(ContentElement(type="hr", attributes=dict(element.attrib)))

    def _process_media_child(self, child: _Element, media_obj: Image) -> None:
        """Process child elements for media objects (Image)."""
        child_tag = self._get_local_name(child.tag)

        if child_tag in ("attachment", "ri:attachment"):
            media_obj.attachment_reference = AttachmentReference(
                filename=self._get_attribute(child, "filename") or "",
                content_id=self._get_attribute(child, "content-id"),
                version_at_save=self._get_attribute(child, "version-at-save"),
            )
        elif child_tag in ("url", "ri:url"):
            media_obj.url_reference = UrlReference(
                value=self._get_attribute(child, "value") or "",
            )
