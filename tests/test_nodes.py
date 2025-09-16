#!/usr/bin/env python3

import pytest

from confluence_content_parser import (
    AttachmentsMacro,
    CodeMacro,
    ConfluenceParser,
    ContainerElement,
    DecisionList,
    DecisionListItem,
    DecisionListItemState,
    DetailsMacro,
    Emoticon,
    ExpandMacro,
    HeadingElement,
    HeadingType,
    Image,
    LayoutElement,
    LinkElement,
    LinkType,
    ListElement,
    ListItem,
    ListType,
    Node,
    PanelMacro,
    PanelMacroType,
    PlaceholderElement,
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


class TestNodeBasics:
    """Test suite for basic node functionality."""

    def test_node_children_default(self):
        """Test default node children behavior."""
        node = Node()
        assert node.get_children() == []

    def test_node_text_default(self):
        """Test default node text behavior."""
        node = Node()
        assert node.to_text() == ""

    def test_node_find_all_empty(self):
        """Test find_all on empty node."""
        node = Node()
        results = node.find_all()
        assert len(results) == 1  # The node itself is returned by walk()
        assert results[0] == node
        assert node.find_all(Text) == []

    def test_container_element_basics(self):
        """Test container element basic functionality."""
        container = ContainerElement()
        assert container.get_children() == []
        assert container.to_text() == ""

    def test_container_element_with_children(self):
        """Test container element with children."""
        text1 = Text(text="Hello")
        text2 = Text(text="World")
        container = ContainerElement(children=[text1, text2])

        assert len(container.get_children()) == 2
        text = container.to_text()
        assert "Hello" in text
        assert "World" in text


class TestTextElements:
    """Test suite for text-related elements."""

    def test_text_element(self):
        """Test text element."""
        text = Text(text="Hello World")
        assert text.to_text() == "Hello World"

    def test_text_break_elements(self):
        """Test text break element types."""
        hr = TextBreakElement(type=TextBreakType.HORIZONTAL_RULE)
        assert hr.to_text() == "---"

        br = TextBreakElement(type=TextBreakType.LINE_BREAK)
        assert br.to_text() == "\n"

    def test_text_effect_elements(self):
        """Test text effect elements."""
        parser = ConfluenceParser()

        # Test strong text
        content = "<strong>Bold text</strong>"
        doc = parser.parse(content)
        effects = doc.find_all(TextEffectElement)
        assert len(effects) == 1
        assert effects[0].type == TextEffectType.STRONG

    def test_heading_elements(self):
        """Test heading elements."""
        parser = ConfluenceParser()

        for level in range(1, 7):
            content = f"<h{level}>Heading {level}</h{level}>"
            doc = parser.parse(content)
            headings = doc.find_all(HeadingElement)
            assert len(headings) == 1
            assert headings[0].type == HeadingType(f"h{level}")


class TestListElements:
    """Test suite for list-related elements."""

    def test_empty_list(self):
        """Test empty list behavior."""
        list_elem = ListElement(type=ListType.UNORDERED)
        assert list_elem.to_text() == ""

    def test_list_with_start_value(self):
        """Test ordered list with start value."""
        parser = ConfluenceParser()
        content = '<ol start="5"><li>Item</li></ol>'
        doc = parser.parse(content)

        lists = doc.find_all(ListElement)
        assert len(lists) == 1
        assert lists[0].start == 5

    def test_task_list_status(self):
        """Test task list item status."""
        parser = ConfluenceParser()
        content = """
        <ac:task-list>
            <ac:task>
                <ac:task-id>1</ac:task-id>
                <ac:task-status>complete</ac:task-status>
                <ac:task-body>Completed task</ac:task-body>
            </ac:task>
        </ac:task-list>
        """
        doc = parser.parse(content)

        items = doc.find_all(ListItem)
        assert len(items) == 1
        assert items[0].status == TaskListItemStatus.COMPLETE

    def test_nested_list_formatting(self):
        """Test complex nested list formatting."""
        parser = ConfluenceParser()
        content = """
        <ul>
            <li>Top level item
                <ul>
                    <li>Nested item 1</li>
                    <li>Nested item 2</li>
                </ul>
            </li>
            <li>Second top item</li>
        </ul>
        """
        doc = parser.parse(content)
        text = doc.text
        assert "Top level item" in text
        assert "Nested item 1" in text
        assert "Nested item 2" in text
        assert "Second top item" in text

    def test_ordered_list_formatting(self):
        """Test ordered list with proper numbering."""
        parser = ConfluenceParser()
        content = """
        <ol>
            <li>First item</li>
            <li>Second item</li>
            <li>Third item</li>
        </ol>
        """
        doc = parser.parse(content)
        text = doc.text
        assert "First item" in text
        assert "Second item" in text
        assert "Third item" in text
        # Should have numbered format
        lists = doc.find_all(ListElement)
        assert len(lists) == 1
        assert lists[0].type == ListType.ORDERED

    def test_ordered_list_direct_numbering(self):
        """Test ordered list numbering increment with direct node creation."""
        from confluence_content_parser.nodes import ListElement, ListItem, ListType, Text

        items = [
            ListItem(children=[Text(text="Item one")]),
            ListItem(children=[Text(text="Item two")]),
            ListItem(children=[Text(text="Item three")]),
        ]
        ordered_list = ListElement(type=ListType.ORDERED, children=items)

        text = ordered_list.to_text()
        assert "1. Item one" in text
        assert "2. Item two" in text
        assert "3. Item three" in text

    def test_task_list_mixed_status(self):
        """Test task list with mixed completion status."""
        parser = ConfluenceParser()
        content = """
        <ac:task-list>
            <ac:task>
                <ac:task-status>complete</ac:task-status>
                <ac:task-body>Completed task</ac:task-body>
            </ac:task>
            <ac:task>
                <ac:task-status>incomplete</ac:task-status>
                <ac:task-body>Incomplete task</ac:task-body>
            </ac:task>
        </ac:task-list>
        """
        doc = parser.parse(content)
        items = doc.find_all(ListItem)
        assert len(items) >= 2

        # Find items with specific statuses
        complete_items = [item for item in items if item.status == TaskListItemStatus.COMPLETE]
        incomplete_items = [item for item in items if item.status == TaskListItemStatus.INCOMPLETE]

        assert len(complete_items) >= 1
        assert len(incomplete_items) >= 1

        # Check text content
        text = doc.text
        assert "Completed task" in text
        assert "Incomplete task" in text

    def test_list_with_mixed_children(self):
        """Test list containing both list items and other elements."""
        parser = ConfluenceParser()
        content = """
        <ul>
            <li>Regular item</li>
            <p>Paragraph in list</p>
        </ul>
        """
        doc = parser.parse(content)
        text = doc.text
        assert "Regular item" in text
        assert "Paragraph in list" in text

    def test_list_item_with_nested_list_element(self):
        """Test ListItem that contains a nested ListElement directly."""
        from confluence_content_parser.nodes import ListElement, ListItem, ListType, Text

        # Create nested structure: ListItem contains both text and nested ListElement
        nested_list = ListElement(type=ListType.UNORDERED, children=[ListItem(children=[Text(text="Nested item")])])
        parent_item = ListItem(children=[Text(text="Parent item"), nested_list])
        parent_list = ListElement(type=ListType.UNORDERED, children=[parent_item])

        text = parent_list.to_text()
        assert "Parent item" in text
        assert "Nested item" in text

    def test_task_list_incomplete_status(self):
        """Test task list with incomplete status."""
        from confluence_content_parser.nodes import ListElement, ListItem, ListType, TaskListItemStatus, Text

        incomplete_item = ListItem(children=[Text(text="Incomplete task")], status=TaskListItemStatus.INCOMPLETE)
        task_list = ListElement(type=ListType.TASK, children=[incomplete_item])

        text = task_list.to_text()
        assert "○ Incomplete task" in text

    def test_list_task_type_fallback(self):
        """Test task list with no status."""
        from confluence_content_parser.nodes import ListElement, ListItem, ListType, Text

        task_item = ListItem(children=[Text(text="Task without status")])
        task_list = ListElement(type=ListType.TASK, children=[task_item])

        text = task_list.to_text()
        assert "Task without status" in text

    def test_list_with_direct_list_element_child(self):
        """Test list that directly contains a ListElement."""
        from confluence_content_parser.nodes import ListElement, ListItem, ListType, Text

        nested_list = ListElement(type=ListType.UNORDERED, children=[ListItem(children=[Text(text="Direct nested")])])
        parent_list = ListElement(type=ListType.UNORDERED, children=[nested_list])

        text = parent_list.to_text()
        assert "Direct nested" in text

    def test_list_with_non_listitem_non_listelement_child(self):
        """Test list that contains other Node types directly."""
        from confluence_content_parser.nodes import ListElement, ListType, Text

        direct_text = Text(text="Direct text in list")
        mixed_list = ListElement(type=ListType.UNORDERED, children=[direct_text])

        text = mixed_list.to_text()
        assert "Direct text in list" in text


class TestLinkElements:
    """Test suite for link-related elements."""

    def test_empty_link(self):
        """Test empty link element."""
        parser = ConfluenceParser()
        content = "<ac:link></ac:link>"
        doc = parser.parse(content)

        links = doc.find_all(LinkElement)
        assert len(links) == 1
        assert links[0].to_text() == ""

    def test_link_with_href_only(self):
        """Test link with href but no children."""
        link = LinkElement(type=LinkType.EXTERNAL, href="https://example.com")
        assert link.to_text() == "https://example.com"

    def test_link_text_combinations(self):
        """Test different link text combinations with direct node creation."""
        # Test link with resource and content parts
        resource_ri = ResourceIdentifier(type=ResourceIdentifierType.PAGE, content_title="TestPage")
        content_text = Text(text="Link Text")
        link_both = LinkElement(type=LinkType.PAGE, children=[resource_ri, content_text])
        text = link_both.to_text()
        assert "📄 Page Link Text" == text

        # Test link with only resource parts
        link_resource = LinkElement(type=LinkType.PAGE, children=[resource_ri])
        text = link_resource.to_text()
        assert "📄 Page" == text

        # Test link with only content parts
        link_content = LinkElement(type=LinkType.PAGE, children=[content_text])
        text = link_content.to_text()
        assert "Link Text" == text

    def test_link_fallback_to_href(self):
        """Test link fallback to href when no usable children."""
        link = LinkElement(type=LinkType.EXTERNAL, href="https://fallback.com", children=[])
        assert link.to_text() == "https://fallback.com"

    def test_link_no_href_no_children_fallback(self):
        """Test link with no href and no usable children."""
        empty_text1 = Text(text="")
        empty_text2 = Text(text="   ")  # whitespace only
        link = LinkElement(type=LinkType.EXTERNAL, children=[empty_text1, empty_text2])
        assert link.to_text() == ""

    def test_resource_identifier_types(self):
        """Test different resource identifier types."""
        parser = ConfluenceParser()
        content = """
        <ac:link>
            <ri:page ri:space-key="TEST" ri:content-title="Page"/>
        </ac:link>
        """
        doc = parser.parse(content)

        identifiers = doc.find_all(ResourceIdentifier)
        assert len(identifiers) == 1
        assert identifiers[0].type == ResourceIdentifierType.PAGE
        assert identifiers[0].space_key == "TEST"
        assert identifiers[0].content_title == "Page"

    def test_resource_identifier_text_representations(self):
        """Test text representations for different resource identifier types."""
        # Test PAGE type
        page_ri = ResourceIdentifier(type=ResourceIdentifierType.PAGE)
        assert page_ri.to_text() == "📄 Page"

        # Test BLOG_POST type with posting_day
        blog_ri = ResourceIdentifier(type=ResourceIdentifierType.BLOG_POST, posting_day="2023-01-01")
        assert blog_ri.to_text() == "📝 Blog: 2023-01-01"

        # Test BLOG_POST type without posting_day
        blog_ri_no_day = ResourceIdentifier(type=ResourceIdentifierType.BLOG_POST)
        assert blog_ri_no_day.to_text() == "📝 Blog"

        # Test ATTACHMENT type with filename
        attachment_ri = ResourceIdentifier(type=ResourceIdentifierType.ATTACHMENT, filename="test.pdf")
        assert attachment_ri.to_text() == "📎 Attachment: test.pdf"

        # Test ATTACHMENT type without filename
        attachment_ri_no_name = ResourceIdentifier(type=ResourceIdentifierType.ATTACHMENT)
        assert attachment_ri_no_name.to_text() == "📎 Attachment"

        # Test URL type with value
        url_ri = ResourceIdentifier(type=ResourceIdentifierType.URL, value="https://example.com")
        assert url_ri.to_text() == "🔗 URL: https://example.com"

        # Test URL type without value
        url_ri_no_val = ResourceIdentifier(type=ResourceIdentifierType.URL)
        assert url_ri_no_val.to_text() == "🔗 URL"

        # Test USER type with account_id
        user_ri = ResourceIdentifier(type=ResourceIdentifierType.USER, account_id="user123")
        assert user_ri.to_text() == "👤 User: user123"

        # Test USER type with userkey
        user_ri_key = ResourceIdentifier(type=ResourceIdentifierType.USER, userkey="userkey123")
        assert user_ri_key.to_text() == "👤 User: userkey123"

        # Test USER type without identifiers
        user_ri_empty = ResourceIdentifier(type=ResourceIdentifierType.USER)
        assert user_ri_empty.to_text() == "👤 User"

        # Test SPACE type with space_key
        space_ri = ResourceIdentifier(type=ResourceIdentifierType.SPACE, space_key="MYSPACE")
        assert space_ri.to_text() == "🏠 Space: MYSPACE"

        # Test SPACE type without space_key
        space_ri_no_key = ResourceIdentifier(type=ResourceIdentifierType.SPACE)
        assert space_ri_no_key.to_text() == "🏠 Space"

        # Test SHORTCUT type with key and parameter
        shortcut_ri = ResourceIdentifier(type=ResourceIdentifierType.SHORTCUT, key="mykey", parameter="param1")
        assert shortcut_ri.to_text() == "🔗 Shortcut: mykey@param1"

        # Test SHORTCUT type without key and parameter
        shortcut_ri_empty = ResourceIdentifier(type=ResourceIdentifierType.SHORTCUT)
        assert shortcut_ri_empty.to_text() == "🔗 Shortcut"

        # Test CONTENT_ENTITY type with content_id
        content_ri = ResourceIdentifier(type=ResourceIdentifierType.CONTENT_ENTITY, content_id="content123")
        assert content_ri.to_text() == "📄 Content: content123"

        # Test CONTENT_ENTITY type without content_id
        content_ri_empty = ResourceIdentifier(type=ResourceIdentifierType.CONTENT_ENTITY)
        assert content_ri_empty.to_text() == "📄 Content"

        # Test version_at_save field
        versioned_ri = ResourceIdentifier(type=ResourceIdentifierType.PAGE, version_at_save="3")
        assert versioned_ri.version_at_save == "3"
        assert hasattr(versioned_ri, "version_at_save")


class TestMacroElementsDirect:
    """Test macro element functionality with direct node construction."""

    def test_code_macro_with_language(self):
        """Test code macro with language specified."""
        from confluence_content_parser.nodes import CodeMacro

        code_macro = CodeMacro(language="python", code="print('hello')")
        text = code_macro.to_text()
        assert text == "```python\nprint('hello')\n```"

    def test_code_macro_without_language(self):
        """Test code macro without language specified."""
        from confluence_content_parser.nodes import CodeMacro

        code_macro = CodeMacro(code="print('hello')")
        text = code_macro.to_text()
        assert text == "```\nprint('hello')\n```"

    def test_code_macro_with_empty_language(self):
        """Test code macro with None language (explicit None)."""
        from confluence_content_parser.nodes import CodeMacro

        code_macro = CodeMacro(language=None, code="test code")
        text = code_macro.to_text()
        assert text == "```\ntest code\n```"

    def test_expand_macro_with_content(self):
        """Test expand macro with content."""
        from confluence_content_parser.nodes import ExpandMacro, Text

        expand = ExpandMacro(title="Click to expand", children=[Text(text="Hidden content")])
        text = expand.to_text()
        assert text == "▶ Click to expand\nHidden content"

    def test_expand_macro_no_content(self):
        """Test expand macro without content."""
        from confluence_content_parser.nodes import ExpandMacro

        expand = ExpandMacro(title="Click to expand", children=[])
        text = expand.to_text()
        assert text == "▶ Click to expand"

    def test_expand_macro_no_title(self):
        """Test expand macro with default title."""
        from confluence_content_parser.nodes import ExpandMacro, Text

        expand = ExpandMacro(children=[Text(text="Hidden content")])
        text = expand.to_text()
        assert text == "▶ Expand\nHidden content"

    def test_expand_macro_explicit_none_title(self):
        """Test expand macro with explicit None title."""
        from confluence_content_parser.nodes import ExpandMacro, Text

        expand = ExpandMacro(title=None, children=[Text(text="Content")])
        text = expand.to_text()
        assert text == "▶ Expand\nContent"

    def test_status_macro_with_colour(self):
        """Test status macro with colour."""
        from confluence_content_parser.nodes import StatusMacro

        status = StatusMacro(title="In Progress", colour="yellow")
        text = status.to_text()
        assert text == "🏷️ Status: In Progress (yellow)"

    def test_status_macro_without_colour(self):
        """Test status macro without colour."""
        from confluence_content_parser.nodes import StatusMacro

        status = StatusMacro(title="Complete")
        text = status.to_text()
        assert text == "🏷️ Status: Complete"

    def test_status_macro_no_title(self):
        """Test status macro with default title."""
        from confluence_content_parser.nodes import StatusMacro

        status = StatusMacro(colour="green")
        text = status.to_text()
        assert text == "🏷️ Status: Status (green)"

    def test_status_macro_explicit_none_title(self):
        """Test status macro with explicit None title."""
        from confluence_content_parser.nodes import StatusMacro

        status = StatusMacro(title=None, colour="blue")
        text = status.to_text()
        assert text == "🏷️ Status: Status (blue)"

    def test_status_macro_no_colour_no_title(self):
        """Test status macro with no title and no colour."""
        from confluence_content_parser.nodes import StatusMacro

        status = StatusMacro()
        text = status.to_text()
        assert text == "🏷️ Status: Status"


class TestMediaElements:
    """Test suite for media-related elements."""

    def test_image_with_src(self):
        """Test image with src attribute."""
        parser = ConfluenceParser()
        content = '<ac:image ac:src="https://example.com/image.jpg"/>'
        doc = parser.parse(content)

        images = doc.find_all(Image)
        assert len(images) == 1
        assert images[0].src == "https://example.com/image.jpg"

    def test_image_with_alt_text(self):
        """Test image with alt text."""
        image = Image(alt="Alt text description")
        text = image.to_text()
        assert "🖼️ Image: Alt text description" in text

    def test_image_with_filename(self):
        """Test image with filename."""
        image = Image(filename="test.png")
        text = image.to_text()
        assert "🖼️ Image: test.png" in text

    def test_image_with_caption(self):
        """Test image with caption children."""
        parser = ConfluenceParser()
        content = """
        <ac:image ac:alt="Test image">
            <ac:caption>This is the image caption</ac:caption>
        </ac:image>
        """
        doc = parser.parse(content)
        images = doc.find_all(Image)
        assert len(images) == 1
        text = images[0].to_text()
        assert "This is the image caption" in text

    def test_image_fallback_unknown(self):
        """Test image fallback to 'Unknown' when no identifiers."""
        image = Image()
        text = image.to_text()
        assert "🖼️ Image: Unknown" in text

    def test_emoticon_element(self):
        """Test emoticon element."""
        parser = ConfluenceParser()
        content = '<ac:emoticon ac:name="smile" ac:emoji-shortname=":smile:"/>'
        doc = parser.parse(content)

        emoticons = doc.find_all(Emoticon)
        assert len(emoticons) == 1
        assert emoticons[0].name == "smile"
        text = emoticons[0].to_text()
        assert ":smile:" in text

    def test_emoticon_fallback_variants(self):
        """Test emoticon fallback to different formats."""
        # Test fallback to emoji_fallback
        emoticon1 = Emoticon(name="smile", emoji_fallback="😊")
        assert emoticon1.to_text() == "😊"

        # Test fallback to emoji_shortname
        emoticon2 = Emoticon(name="wink", emoji_shortname=":wink:")
        assert emoticon2.to_text() == ":wink:"

        # Test fallback to name format
        emoticon3 = Emoticon(name="thumbs_up")
        assert emoticon3.to_text() == ":thumbs_up:"

    def test_time_element(self):
        """Test time element."""
        parser = ConfluenceParser()
        content = '<time datetime="2023-01-01">January 1, 2023</time>'
        doc = parser.parse(content)

        times = doc.find_all(Time)
        assert len(times) == 1
        assert times[0].datetime == "2023-01-01"
        assert "📅" in times[0].to_text()

    def test_time_element_without_datetime(self):
        """Test time element without datetime attribute."""
        time_elem = Time()
        text = time_elem.to_text()
        assert text == "📅 Date"


class TestTableElements:
    """Test suite for table-related elements."""

    def test_table_structure(self):
        """Test table element parsing."""
        parser = ConfluenceParser()
        content = """
        <table>
            <tbody>
                <tr>
                    <th>Header</th>
                    <td>Cell</td>
                </tr>
            </tbody>
        </table>
        """
        doc = parser.parse(content)

        tables = doc.find_all(Table)
        assert len(tables) == 1

        rows = doc.find_all(TableRow)
        assert len(rows) == 1

        cells = doc.find_all(TableCell)
        assert len(cells) == 2

    def test_empty_table(self):
        """Test empty table behavior."""
        table = Table()
        assert table.to_text() == ""

    def test_table_with_multiple_rows(self):
        """Test table with multiple rows."""
        parser = ConfluenceParser()
        content = """
        <table>
            <tbody>
                <tr><td>Row 1 Cell 1</td><td>Row 1 Cell 2</td></tr>
                <tr><td>Row 2 Cell 1</td><td>Row 2 Cell 2</td></tr>
            </tbody>
        </table>
        """
        doc = parser.parse(content)

        tables = doc.find_all(Table)
        assert len(tables) == 1
        table_text = tables[0].to_text()
        assert "Row 1 Cell 1" in table_text
        assert "Row 2 Cell 1" in table_text

    def test_table_row_formatting(self):
        """Test table row text formatting."""
        parser = ConfluenceParser()
        content = """
        <tr>
            <td>Cell 1</td>
            <td>Cell 2</td>
            <td>Cell 3</td>
        </tr>
        """
        doc = parser.parse(content)

        rows = doc.find_all(TableRow)
        assert len(rows) == 1
        row_text = rows[0].to_text()
        assert "|" in row_text  # Should use pipe separator
        assert "Cell 1" in row_text
        assert "Cell 3" in row_text

    def test_empty_table_row(self):
        """Test empty table row behavior."""
        row = TableRow()
        assert row.to_text() == ""

    def test_table_cell_attributes(self):
        """Test table cell with attributes."""
        cell = TableCell(is_header=True, rowspan=2, colspan=3)
        assert cell.is_header is True
        assert cell.rowspan == 2
        assert cell.colspan == 3


class TestLayoutElements:
    """Test suite for layout-related elements."""

    def test_layout_structure(self):
        """Test layout element parsing."""
        parser = ConfluenceParser()
        content = """
        <ac:layout>
            <ac:layout-section ac:type="single">
                <ac:layout-cell>
                    <p>Content</p>
                </ac:layout-cell>
            </ac:layout-section>
        </ac:layout>
        """
        doc = parser.parse(content)

        layouts = doc.find_all(LayoutElement)
        assert len(layouts) == 1

        # Test that layout parsing succeeded
        assert "Content" in doc.text


class TestMacroElements:
    """Test suite for macro-related elements."""

    def test_placeholder_element(self):
        """Test placeholder element."""
        parser = ConfluenceParser()
        content = '<ac:placeholder ac:type="text">Placeholder text</ac:placeholder>'
        doc = parser.parse(content)

        placeholders = doc.find_all(PlaceholderElement)
        assert len(placeholders) == 1
        assert "Placeholder:" in placeholders[0].to_text()

    def test_status_macro(self):
        """Test status macro."""
        parser = ConfluenceParser()
        content = """
        <ac:structured-macro ac:name="status">
            <ac:parameter ac:name="title">Done</ac:parameter>
            <ac:parameter ac:name="colour">Green</ac:parameter>
        </ac:structured-macro>
        """
        doc = parser.parse(content)

        statuses = doc.find_all(StatusMacro)
        assert len(statuses) == 1
        assert statuses[0].title == "Done"
        assert statuses[0].colour == "Green"

    def test_panel_macro_types(self):
        """Test different panel macro types."""
        parser = ConfluenceParser()
        content = """
        <ac:structured-macro ac:name="info">
            <ac:rich-text-body>
                <p>Info panel content</p>
            </ac:rich-text-body>
        </ac:structured-macro>
        """
        doc = parser.parse(content)

        panels = doc.find_all(PanelMacro)
        assert len(panels) == 1
        assert panels[0].type == PanelMacroType.INFO

    def test_panel_macro_text_representations(self):
        """Test text representations for different panel types."""
        # Test NOTE panel with content
        note_panel = PanelMacro(type=PanelMacroType.NOTE, children=[Text(text="Note content")])
        text = note_panel.to_text()
        assert "📝 NOTE:" in text and "Note content" in text

        # Test NOTE panel without content
        empty_note = PanelMacro(type=PanelMacroType.NOTE)
        assert empty_note.to_text() == "📝 NOTE"

        # Test SUCCESS panel
        success_panel = PanelMacro(type=PanelMacroType.SUCCESS, children=[Text(text="Success!")])
        text = success_panel.to_text()
        assert "✅ SUCCESS:" in text and "Success!" in text

        # Test SUCCESS panel without content
        empty_success = PanelMacro(type=PanelMacroType.SUCCESS)
        assert empty_success.to_text() == "✅ SUCCESS"

        # Test WARNING panel
        warning_panel = PanelMacro(type=PanelMacroType.WARNING, children=[Text(text="Warning message")])
        text = warning_panel.to_text()
        assert "⚠️ WARNING:" in text and "Warning message" in text

        # Test WARNING panel without content
        empty_warning = PanelMacro(type=PanelMacroType.WARNING)
        assert empty_warning.to_text() == "⚠️ WARNING"

        # Test ERROR panel
        error_panel = PanelMacro(type=PanelMacroType.ERROR, children=[Text(text="Error occurred")])
        text = error_panel.to_text()
        assert "❌ ERROR:" in text and "Error occurred" in text

        # Test ERROR panel without content
        empty_error = PanelMacro(type=PanelMacroType.ERROR)
        assert empty_error.to_text() == "❌ ERROR"

        # Test INFO panel
        info_panel = PanelMacro(type=PanelMacroType.INFO, children=[Text(text="Information")])
        text = info_panel.to_text()
        assert "ℹ️ INFO:" in text and "Information" in text

        # Test INFO panel without content
        empty_info = PanelMacro(type=PanelMacroType.INFO)
        assert empty_info.to_text() == "ℹ️ INFO"

        # Test PANEL with custom icon text
        panel_with_icon = PanelMacro(
            type=PanelMacroType.PANEL, panel_icon_text="🎯", children=[Text(text="Custom panel")]
        )
        text = panel_with_icon.to_text()
        assert "🎯" in text and "Custom panel" in text

        # Test PANEL with custom icon text but no content
        panel_icon_only = PanelMacro(type=PanelMacroType.PANEL, panel_icon_text="🎯")
        assert panel_icon_only.to_text() == "🎯"

        # Test PANEL without custom icon
        basic_panel = PanelMacro(type=PanelMacroType.PANEL, children=[Text(text="Basic panel")])
        text = basic_panel.to_text()
        assert "📋 PANEL:" in text and "Basic panel" in text

        # Test PANEL without custom icon and no content
        empty_panel = PanelMacro(type=PanelMacroType.PANEL)
        assert empty_panel.to_text() == "📋 PANEL"

    def test_code_macro(self):
        """Test code macro with language."""
        parser = ConfluenceParser()
        content = """
        <ac:structured-macro ac:name="code">
            <ac:parameter ac:name="language">python</ac:parameter>
            <ac:plain-text-body>print("hello")</ac:plain-text-body>
        </ac:structured-macro>
        """
        doc = parser.parse(content)

        codes = doc.find_all(CodeMacro)
        assert len(codes) == 1
        assert codes[0].language == "python"

    def test_expand_macro(self):
        """Test expand macro."""
        parser = ConfluenceParser()
        content = """
        <ac:structured-macro ac:name="expand">
            <ac:parameter ac:name="title">Click to expand</ac:parameter>
            <ac:rich-text-body>
                <p>Hidden content</p>
            </ac:rich-text-body>
        </ac:structured-macro>
        """
        doc = parser.parse(content)

        expands = doc.find_all(ExpandMacro)
        assert len(expands) == 1
        assert expands[0].title == "Click to expand"

    def test_details_macro(self):
        """Test details macro."""
        parser = ConfluenceParser()
        content = """
        <ac:macro ac:name="details">
            <ac:rich-text-body>
                <p>Details content</p>
            </ac:rich-text-body>
        </ac:macro>
        """
        doc = parser.parse(content)

        details = doc.find_all(DetailsMacro)
        assert len(details) == 1
        assert "Details:" in details[0].to_text()

    def test_toc_macro(self):
        """Test table of contents macro."""
        parser = ConfluenceParser()
        content = """
        <ac:structured-macro ac:name="toc">
            <ac:parameter ac:name="style">table</ac:parameter>
        </ac:structured-macro>
        """
        doc = parser.parse(content)

        tocs = doc.find_all(TocMacro)
        assert len(tocs) == 1
        assert "Table of Contents" in tocs[0].to_text()

    def test_attachments_macro(self):
        """Test attachments macro."""
        parser = ConfluenceParser()
        content = """
        <ac:structured-macro ac:name="attachments">
            <ac:parameter ac:name="patterns">*.pdf</ac:parameter>
        </ac:structured-macro>
        """
        doc = parser.parse(content)

        attachments = doc.find_all(AttachmentsMacro)
        assert len(attachments) == 1
        assert "Attachments" in attachments[0].to_text()

    def test_viewpdf_macro(self):
        """Test viewpdf macro."""
        parser = ConfluenceParser()
        content = """
        <ac:structured-macro ac:name="viewpdf">
            <ac:parameter ac:name="name">
                <ri:attachment ri:filename="doc.pdf" ri:version-at-save="1"/>
            </ac:parameter>
        </ac:structured-macro>
        """
        doc = parser.parse(content)

        pdfs = doc.find_all(ViewPdfMacro)
        assert len(pdfs) == 1
        assert pdfs[0].filename == "doc.pdf"

    def test_view_file_macro(self):
        """Test view-file macro."""
        parser = ConfluenceParser()
        content = """
        <ac:structured-macro ac:name="view-file">
            <ac:parameter ac:name="name">
                <ri:attachment ri:filename="spreadsheet.xlsx"/>
            </ac:parameter>
        </ac:structured-macro>
        """
        doc = parser.parse(content)

        files = doc.find_all(ViewFileMacro)
        assert len(files) == 1
        assert files[0].filename == "spreadsheet.xlsx"

    def test_tasks_report_macro(self):
        """Test tasks report macro."""
        parser = ConfluenceParser()
        content = """
        <ac:structured-macro ac:name="tasks-report-macro">
            <ac:parameter ac:name="isMissingRequiredParameters">false</ac:parameter>
        </ac:structured-macro>
        """
        doc = parser.parse(content)

        tasks = doc.find_all(TasksReportMacro)
        assert len(tasks) == 1
        assert tasks[0].is_missing_required_parameters is False


class TestDecisionElements:
    """Test suite for decision-related elements."""

    def test_decision_list(self):
        """Test decision list parsing."""
        parser = ConfluenceParser()
        content = """
        <ac:adf-extension>
            <ac:adf-node type="decision-list">
                <ac:adf-attribute key="local-id">decision-1</ac:adf-attribute>
                <ac:adf-node type="decision-item">
                    <ac:adf-attribute key="local-id">item-1</ac:adf-attribute>
                    <ac:adf-attribute key="state">DECIDED</ac:adf-attribute>
                    <ac:adf-content>Decision item</ac:adf-content>
                </ac:adf-node>
            </ac:adf-node>
        </ac:adf-extension>
        """
        doc = parser.parse(content)

        decisions = doc.find_all(DecisionList)
        assert len(decisions) == 1

        items = doc.find_all(DecisionListItem)
        assert len(items) == 1
        assert items[0].state == DecisionListItemState.DECIDED


class TestMacroElementsAdditional:
    """Test additional macro element functionality."""

    def test_jira_macro_variants(self):
        """Test JIRA macro text representations."""
        from confluence_content_parser.nodes import JiraMacro

        # Test with key and non-system server
        jira1 = JiraMacro(key="PROJ-123", server="Custom Jira")
        assert jira1.to_text() == "🎫 PROJ-123 (Custom Jira)"

        # Test with key and system server
        jira2 = JiraMacro(key="PROJ-456", server="System Jira")
        assert jira2.to_text() == "🎫 PROJ-456"

        # Test with key and no server
        jira3 = JiraMacro(key="PROJ-789")
        assert jira3.to_text() == "🎫 PROJ-789"

        # Test without key
        jira4 = JiraMacro()
        assert jira4.to_text() == "🎫 JIRA Issue"

    def test_include_macro_variants(self):
        """Test include macro text representations."""
        from confluence_content_parser.nodes import IncludeMacro

        # Test with content title
        include1 = IncludeMacro(content_title="My Page")
        assert include1.to_text() == "📄 Include: My Page"

        # Test without content title
        include2 = IncludeMacro()
        assert include2.to_text() == "📄 Include Page"

    def test_tasks_report_macro_variants(self):
        """Test tasks report macro text representations."""
        from confluence_content_parser.nodes import TasksReportMacro

        # Test with spaces
        tasks1 = TasksReportMacro(spaces="SPACE1,SPACE2")
        assert tasks1.to_text() == "📊 Tasks Report: SPACE1,SPACE2"

        # Test without spaces
        tasks2 = TasksReportMacro()
        assert tasks2.to_text() == "📊 Tasks Report"

    def test_excerpt_include_macro_variants(self):
        """Test excerpt include macro text representations."""
        from confluence_content_parser.nodes import ExcerptIncludeMacro

        # Test with content title and posting day
        excerpt1 = ExcerptIncludeMacro(content_title="Blog Post", posting_day="2023-01-01")
        assert excerpt1.to_text() == "📝 Excerpt: Blog Post (2023-01-01)"

        # Test with content title but no posting day
        excerpt2 = ExcerptIncludeMacro(content_title="Regular Page")
        assert excerpt2.to_text() == "📝 Excerpt: Regular Page"

        # Test without content title
        excerpt3 = ExcerptIncludeMacro()
        assert excerpt3.to_text() == "📝 Excerpt Include"

    def test_viewpdf_macro_variants(self):
        """Test viewpdf macro text representations."""
        from confluence_content_parser.nodes import ViewPdfMacro

        # Test with filename
        pdf1 = ViewPdfMacro(filename="document.pdf")
        assert pdf1.to_text() == "📄 PDF: document.pdf"

        # Test without filename
        pdf2 = ViewPdfMacro()
        assert pdf2.to_text() == "📄 PDF Viewer"

    def test_viewfile_macro_variants(self):
        """Test viewfile macro text representations."""
        from confluence_content_parser.nodes import ViewFileMacro

        # Test with filename
        file1 = ViewFileMacro(filename="spreadsheet.xlsx")
        assert file1.to_text() == "📁 File: spreadsheet.xlsx"

        # Test without filename
        file2 = ViewFileMacro()
        assert file2.to_text() == "📁 File Viewer"

    def test_profile_macro_variants(self):
        """Test profile macro text representations."""
        from confluence_content_parser.nodes import ProfileMacro

        # Test with account_id
        profile1 = ProfileMacro(account_id="user123")
        assert profile1.to_text() == "👤 Profile: user123"

        # Test without account_id
        profile2 = ProfileMacro()
        assert profile2.to_text() == "👤 User Profile"

    def test_anchor_macro_variants(self):
        """Test anchor macro text representations."""
        from confluence_content_parser.nodes import AnchorMacro

        # Test with anchor name
        anchor1 = AnchorMacro(anchor_name="section1")
        assert anchor1.to_text() == "⚓ Anchor: section1"

        # Test without anchor name
        anchor2 = AnchorMacro()
        assert anchor2.to_text() == "⚓ Anchor"

    def test_excerpt_macro_variants(self):
        """Test excerpt macro text representations."""
        from confluence_content_parser.nodes import ExcerptMacro, Text

        # Test with content
        excerpt1 = ExcerptMacro(children=[Text(text="Excerpt content")])
        assert excerpt1.to_text() == "📄 Excerpt: Excerpt content"

        # Test without content
        excerpt2 = ExcerptMacro()
        assert excerpt2.to_text() == "📄 Excerpt"

    def test_decision_list_variants(self):
        """Test decision list text representations."""
        from confluence_content_parser.nodes import DecisionList, DecisionListItem, Text

        # Test empty decision list
        decision_list1 = DecisionList()
        assert decision_list1.to_text() == "📋 Decision List"

        # Test decision list with items
        item = DecisionListItem(children=[Text(text="Decision item")])
        decision_list2 = DecisionList(children=[item])
        text = decision_list2.to_text()
        assert "Decision item" in text

    def test_decision_list_item_variants(self):
        """Test decision list item text representations."""
        from confluence_content_parser.nodes import DecisionListItem, DecisionListItemState, Text

        # Test decided item with content
        decided_item = DecisionListItem(state=DecisionListItemState.DECIDED, children=[Text(text="Decided item")])
        assert decided_item.to_text() == "✅ Decided item"

        # Test decided item without content
        decided_empty = DecisionListItem(state=DecisionListItemState.DECIDED)
        assert decided_empty.to_text() == "✅"

        # Test pending item with content
        pending_item = DecisionListItem(state=DecisionListItemState.PENDING, children=[Text(text="Pending item")])
        assert pending_item.to_text() == "⏳ Pending item"

        # Test pending item without content (or no state)
        pending_empty = DecisionListItem()
        assert pending_empty.to_text() == "⏳"


if __name__ == "__main__":
    pytest.main([__file__])
