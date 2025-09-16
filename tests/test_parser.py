#!/usr/bin/env python3

import pytest

from confluence_content_parser import (
    AnchorMacro,
    CodeMacro,
    ConfluenceDocument,
    ConfluenceParser,
    DecisionListItem,
    DecisionListItemState,
    ExcerptIncludeMacro,
    ExcerptMacro,
    ExpandMacro,
    Fragment,
    HeadingElement,
    Image,
    IncludeMacro,
    JiraMacro,
    LinkElement,
    LinkType,
    ListElement,
    ListItem,
    PanelMacro,
    PanelMacroType,
    ParsingError,
    ProfileMacro,
    ResourceIdentifier,
    TasksReportMacro,
    TextBreakElement,
    TextBreakType,
)


class TestConfluenceParser:
    """Test suite for ConfluenceParser class."""

    def test_parser_initialization_default(self):
        """Test parser initialization with default parameters."""
        parser = ConfluenceParser()
        assert parser.raise_on_finish is True
        assert parser.diagnostics == []
        assert parser.NS_AC == "http://www.atlassian.com/schema/confluence/4/ac/"
        assert parser.NS_RI == "http://www.atlassian.com/schema/confluence/4/ri/"
        assert parser.NS_AT == "http://www.atlassian.com/schema/confluence/4/at/"

    def test_parser_initialization_custom(self):
        """Test parser initialization with custom parameters."""
        parser = ConfluenceParser(raise_on_finish=False)
        assert parser.raise_on_finish is False
        assert parser.diagnostics == []

    def test_parse_empty_content(self):
        """Test parsing empty content."""
        parser = ConfluenceParser(raise_on_finish=False)
        doc = parser.parse("")
        assert isinstance(doc, ConfluenceDocument)
        assert doc.root is None
        assert doc.text == ""

    def test_parse_whitespace_only(self):
        """Test parsing whitespace-only content."""
        parser = ConfluenceParser(raise_on_finish=False)
        doc = parser.parse("   \n\t  ")
        assert isinstance(doc, ConfluenceDocument)
        assert doc.root is None

    def test_parse_simple_text(self):
        """Test parsing simple text content."""
        parser = ConfluenceParser()
        doc = parser.parse("<p>Hello world</p>")
        assert doc.root is not None
        assert "Hello world" in doc.text

    def test_parse_with_diagnostics_disabled(self):
        """Test parsing with diagnostics collection disabled."""
        parser = ConfluenceParser(raise_on_finish=False)
        doc = parser.parse("<unknown-element>test</unknown-element>")
        assert isinstance(doc, ConfluenceDocument)
        assert "unknown_element:unknown-element" in doc.metadata.get("diagnostics", [])

    def test_parse_with_diagnostics_enabled_raises(self):
        """Test parsing with diagnostics enabled raises on unknown elements."""
        parser = ConfluenceParser(raise_on_finish=True)
        with pytest.raises(ParsingError) as exc_info:
            parser.parse("<unknown-element>test</unknown-element>")
        assert len(exc_info.value.diagnostics) > 0

    def test_unicode_surrogate_handling(self):
        """Test handling of Unicode surrogate characters."""
        parser = ConfluenceParser(raise_on_finish=False)
        # Test the fix_unicode_surrogates method with normal content
        test_content = "test content"
        result = parser._fix_unicode_surrogates(test_content)
        assert result == test_content

        # Test with content that has problematic characters
        # Create a string with high surrogate that would cause issues
        problematic_content = "test \ud800 content"  # high surrogate
        result = parser._fix_unicode_surrogates(problematic_content)
        # Should remove the problematic character
        assert result == "test  content"


class TestParserUtilities:
    """Test suite for parser utility methods."""

    def test_get_tag_name(self):
        """Test tag name extraction utility."""
        parser = ConfluenceParser()

        # Test with namespace
        from xml.etree import ElementTree as ET

        element_with_ns = ET.fromstring('<ns:tag xmlns:ns="namespace">content</ns:tag>')
        tag_name = parser._get_tag_name(element_with_ns)
        assert tag_name == "tag"

        # Test without namespace
        element_without_ns = ET.fromstring("<tag>content</tag>")
        tag_name = parser._get_tag_name(element_without_ns)
        assert tag_name == "tag"

    def test_get_attr(self):
        """Test attribute extraction utility."""
        parser = ConfluenceParser()
        from xml.etree import ElementTree as ET

        # Test normal attribute
        element = ET.fromstring('<tag attr="value">content</tag>')
        attr_value = parser._get_attr(element, "attr")
        assert attr_value == "value"

        # Test missing attribute
        missing_value = parser._get_attr(element, "missing")
        assert missing_value is None

    def test_find_child_by_tag(self):
        """Test child finding utility."""
        parser = ConfluenceParser()
        from xml.etree import ElementTree as ET

        root = ET.fromstring("<root><child1>content1</child1><child2>content2</child2></root>")
        child = parser._find_child_by_tag(root, "child1")
        assert child is not None
        assert child.text == "content1"

        missing_child = parser._find_child_by_tag(root, "missing")
        assert missing_child is None

    def test_extract_text_content(self):
        """Test text content extraction utility."""
        parser = ConfluenceParser()
        from xml.etree import ElementTree as ET

        element = ET.fromstring("<root>Start <child>middle</child> end</root>")
        text = parser._extract_text_content(element)
        assert "Start" in text
        assert "middle" in text
        assert "end" in text

    def test_iter_parameters(self):
        """Test parameter iteration utility."""
        parser = ConfluenceParser()
        from xml.etree import ElementTree as ET

        root = ET.fromstring(
            """
        <macro>
            <parameter name="param1">value1</parameter>
            <parameter name="param2">value2</parameter>
            <other>not-a-param</other>
        </macro>
        """
        )

        params = list(parser._iter_parameters(root))
        assert len(params) == 2

    def test_css_style_parsing_edge_cases(self):
        """Test CSS style parsing with edge cases."""
        parser = ConfluenceParser()
        from xml.etree import ElementTree as ET

        # Test empty style
        element = ET.fromstring('<div style="">content</div>')
        styles = parser._parse_css_styles(element)
        assert len(styles) == 0

        # Test malformed style
        element = ET.fromstring('<div style="color; invalid:;">content</div>')
        styles = parser._parse_css_styles(element)
        assert len(styles) == 0

        # Test proper style
        element = ET.fromstring('<div style="color: red; margin: 10px;">content</div>')
        styles = parser._parse_css_styles(element)
        assert styles["color"] == "red"
        assert styles["margin"] == "10px"


class TestParserComplexScenarios:
    """Test suite for complex parsing scenarios."""

    def test_consolidate_root_multiple_children(self):
        """Test root consolidation with multiple children."""
        parser = ConfluenceParser()
        content = "<h1>Title</h1><p>Paragraph</p>"
        doc = parser.parse(content)

        # Should create a Fragment to contain multiple children
        assert doc.root is not None
        assert isinstance(doc.root, Fragment)

    def test_consolidate_root_single_child(self):
        """Test root consolidation with single child."""
        parser = ConfluenceParser()
        content = "<h1>Title</h1>"
        doc = parser.parse(content)

        # Should return the single child directly
        assert isinstance(doc.root, HeadingElement)

    def test_tasks_report_macro_boolean_parsing(self):
        """Test tasks report macro with boolean parameter parsing."""
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

    def test_panel_macro_type_mapping(self):
        """Test panel macro type mapping for different panel names."""
        parser = ConfluenceParser()

        # Test tip panel
        tip_content = """
        <ac:structured-macro ac:name="tip">
            <ac:rich-text-body><p>Tip content</p></ac:rich-text-body>
        </ac:structured-macro>
        """
        doc = parser.parse(tip_content)
        panels = doc.find_all(PanelMacro)
        assert len(panels) == 1
        assert panels[0].type == PanelMacroType.SUCCESS

        # Test note panel
        note_content = """
        <ac:structured-macro ac:name="note">
            <ac:rich-text-body><p>Note content</p></ac:rich-text-body>
        </ac:structured-macro>
        """
        doc = parser.parse(note_content)
        panels = doc.find_all(PanelMacro)
        assert len(panels) == 1
        assert panels[0].type == PanelMacroType.WARNING

        # Test warning panel
        warning_content = """
        <ac:structured-macro ac:name="warning">
            <ac:rich-text-body><p>Warning content</p></ac:rich-text-body>
        </ac:structured-macro>
        """
        doc = parser.parse(warning_content)
        panels = doc.find_all(PanelMacro)
        assert len(panels) == 1
        assert panels[0].type == PanelMacroType.ERROR

    def test_panel_macro_parameters(self):
        """Test panel macro with various parameters."""
        parser = ConfluenceParser()
        content = """
        <ac:structured-macro ac:name="panel">
            <ac:parameter ac:name="bgColor">#FFE6E6</ac:parameter>
            <ac:parameter ac:name="panelIcon">⚠️</ac:parameter>
            <ac:parameter ac:name="panelIconId">warning-icon</ac:parameter>
            <ac:parameter ac:name="panelIconText">Warning</ac:parameter>
            <ac:rich-text-body><p>Panel content</p></ac:rich-text-body>
        </ac:structured-macro>
        """
        doc = parser.parse(content)

        panels = doc.find_all(PanelMacro)
        assert len(panels) == 1
        panel = panels[0]
        assert panel.bg_color == "#FFE6E6"
        assert panel.panel_icon == "⚠️"
        assert panel.panel_icon_id == "warning-icon"
        assert panel.panel_icon_text == "Warning"


class TestParserErrorHandling:
    """Test suite for parser error handling."""

    def test_xml_parse_error(self):
        """Test handling of XML parse errors."""
        parser = ConfluenceParser(raise_on_finish=False)
        content = "<invalid-xml"
        doc = parser.parse(content)

        diagnostics = doc.metadata.get("diagnostics", [])
        assert any("XML parsing failed" in d for d in diagnostics)

    def test_skipped_elements(self):
        """Test that certain elements are skipped without generating diagnostics."""
        parser = ConfluenceParser(raise_on_finish=False)
        content = """
        <table>
            <colgroup>
                <col style="width: 100px;"/>
            </colgroup>
            <tr><td>Content</td></tr>
        </table>
        <p>Text with <ac:inline-comment-marker>comment</ac:inline-comment-marker></p>
        """
        doc = parser.parse(content)

        # These elements should be skipped without diagnostics
        diagnostics = doc.metadata.get("diagnostics", [])
        skipped_elements = ["colgroup", "col", "inline-comment-marker"]
        for element in skipped_elements:
            assert not any(element in d for d in diagnostics)

    def test_invalid_list_start_attribute(self):
        """Test handling of invalid start attribute in ordered list."""
        parser = ConfluenceParser()
        content = '<ol start="not-a-number"><li>Item</li></ol>'
        doc = parser.parse(content)

        lists = doc.find_all(ListElement)
        assert len(lists) == 1
        # Start should be None when parsing fails
        assert lists[0].start is None

    def test_unknown_macro_handling(self):
        """Test handling of unknown macros."""
        parser = ConfluenceParser(raise_on_finish=False)
        content = """
        <ac:structured-macro ac:name="unknown-macro">
            <ac:parameter ac:name="param">value</ac:parameter>
            <ac:rich-text-body>
                <p>Content</p>
            </ac:rich-text-body>
        </ac:structured-macro>
        """
        doc = parser.parse(content)
        diagnostics = doc.metadata.get("diagnostics", [])
        assert any("unknown_macro:unknown-macro" in d for d in diagnostics)

    def test_unknown_element_handling(self):
        """Test handling of unknown elements."""
        parser = ConfluenceParser(raise_on_finish=False)
        content = "<unknown-element>content</unknown-element>"
        doc = parser.parse(content)
        diagnostics = doc.metadata.get("diagnostics", [])
        assert any("unknown_element:unknown-element" in d for d in diagnostics)

    def test_adf_extension_without_adf_node(self):
        """Test ADF extension without adf-node child."""
        parser = ConfluenceParser(raise_on_finish=False)
        content = """
        <ac:adf-extension>
            <p>Content without adf-node</p>
        </ac:adf-extension>
        """
        doc = parser.parse(content)
        # ADF extension without adf-node returns None, so root should be None
        assert doc.root is None

    def test_adf_panel_parsing(self):
        """Test ADF panel parsing."""
        parser = ConfluenceParser(raise_on_finish=False)
        content = """
        <ac:adf-extension>
            <ac:adf-node type="panel">
                <ac:adf-attribute key="panel-type">info</ac:adf-attribute>
                <ac:adf-content>
                    <p>ADF Panel content</p>
                </ac:adf-content>
            </ac:adf-node>
        </ac:adf-extension>
        """
        doc = parser.parse(content)

        panels = doc.find_all(PanelMacro)
        assert len(panels) == 1

    def test_adf_decision_item_parsing(self):
        """Test ADF decision item parsing."""
        parser = ConfluenceParser(raise_on_finish=False)
        content = """
        <ac:adf-extension>
            <ac:adf-node type="decision-item">
                <ac:adf-attribute key="state">DECIDED</ac:adf-attribute>
                <ac:adf-content>Decision content</ac:adf-content>
            </ac:adf-node>
        </ac:adf-extension>
        """
        doc = parser.parse(content)

        items = doc.find_all(DecisionListItem)
        assert len(items) == 1
        assert items[0].state == DecisionListItemState.DECIDED

    def test_unknown_adf_node_type(self):
        """Test unknown ADF node type handling."""
        parser = ConfluenceParser(raise_on_finish=False)
        content = """
        <ac:adf-extension>
            <ac:adf-node type="unknown-type">
                <ac:adf-content>Unknown content</ac:adf-content>
            </ac:adf-node>
        </ac:adf-extension>
        """
        doc = parser.parse(content)

        diagnostics = doc.metadata.get("diagnostics", [])
        assert "unknown_adf_node_type:unknown-type" in diagnostics

    def test_text_break_elements_without_styles(self):
        """Test parsing hr/br elements without styles."""
        parser = ConfluenceParser()
        content = "<hr/><br/>"
        doc = parser.parse(content)

        breaks = doc.find_all(TextBreakElement)
        assert len(breaks) == 2
        assert breaks[0].type == TextBreakType.HORIZONTAL_RULE
        assert breaks[1].type == TextBreakType.LINE_BREAK


class TestParserMacroHandling:
    """Test parser handling of macros and elements."""

    def test_task_parsing_with_uuid(self):
        """Test task parsing with uuid element."""
        parser = ConfluenceParser()
        content = """
        <ac:task-list>
            <ac:task>
                <ac:task-id>task1</ac:task-id>
                <ac:task-uuid>uuid-123</ac:task-uuid>
                <ac:task-status>complete</ac:task-status>
                <ac:task-body>Task with UUID</ac:task-body>
            </ac:task>
        </ac:task-list>
        """
        doc = parser.parse(content)
        items = doc.find_all(ListItem)
        assert len(items) >= 1
        task_item = next((item for item in items if item.uuid), None)
        assert task_item is not None
        assert task_item.uuid == "uuid-123"

    def test_link_parsing_coverage(self):
        """Test link parsing to cover missing lines."""
        parser = ConfluenceParser()
        # Test various link type detections
        test_cases = [
            ('<ac:link><ri:page ri:content-title="Page"/></ac:link>', LinkType.PAGE),
            ('<ac:link><ri:blog-post ri:content-title="Post"/></ac:link>', LinkType.BLOG_POST),
            ('<ac:link><ri:user ri:account-id="user1"/></ac:link>', LinkType.USER),
            ('<ac:link><ri:space ri:space-key="SPACE"/></ac:link>', LinkType.SPACE),
            ('<ac:link><ri:attachment ri:filename="file.pdf"/></ac:link>', LinkType.ATTACHMENT),
            ('<ac:link ac:anchor="section1">Anchor link</ac:link>', LinkType.ANCHOR),
        ]

        for content, expected_type in test_cases:
            doc = parser.parse(content)
            links = doc.find_all(LinkElement)
            assert len(links) >= 1
            assert links[0].type == expected_type

    def test_image_parsing_url_element(self):
        """Test image parsing with URL element."""
        parser = ConfluenceParser()
        content = """
        <ac:image>
            <ri:url ri:value="https://example.com/image.jpg"/>
        </ac:image>
        """
        doc = parser.parse(content)
        images = doc.find_all(Image)
        assert len(images) == 1
        assert images[0].url_value == "https://example.com/image.jpg"

    def test_unknown_macro_simple(self):
        """Test simple unknown macro handling."""
        parser = ConfluenceParser(raise_on_finish=False)
        content = """
        <ac:macro ac:name="unknown-simple-macro">
            <ac:parameter ac:name="param">value</ac:parameter>
        </ac:macro>
        """
        doc = parser.parse(content)
        diagnostics = doc.metadata.get("diagnostics", [])
        assert any("unknown_macro:unknown-simple-macro" in d for d in diagnostics)

    def test_adf_panel_with_bgcolor(self):
        """Test ADF panel with background color."""
        parser = ConfluenceParser(raise_on_finish=False)
        content = """
        <ac:adf-extension>
            <ac:adf-node type="panel">
                <ac:adf-attribute key="panel-type">note</ac:adf-attribute>
                <ac:adf-attribute key="bg-color">#E3FCEF</ac:adf-attribute>
                <ac:adf-content>
                    <p>Panel with background</p>
                </ac:adf-content>
            </ac:adf-node>
        </ac:adf-extension>
        """
        doc = parser.parse(content)
        panels = doc.find_all(PanelMacro)
        assert len(panels) == 1
        assert panels[0].bg_color == "#E3FCEF"

    def test_macro_parameter_parsing(self):
        """Test macro parameter parsing edge cases."""
        parser = ConfluenceParser()

        # Test expand macro with breakout width parameter
        content1 = """
        <ac:structured-macro ac:name="expand">
            <ac:parameter ac:name="title">Test Title</ac:parameter>
            <ac:parameter ac:name="breakoutWidth">wide</ac:parameter>
            <ac:rich-text-body><p>Content</p></ac:rich-text-body>
        </ac:structured-macro>
        """
        doc1 = parser.parse(content1)
        expands = doc1.find_all(ExpandMacro)
        assert len(expands) == 1
        assert expands[0].title == "Test Title"
        assert expands[0].breakout_width == "wide"

        # Test code macro with breakout parameters
        content2 = """
        <ac:structured-macro ac:name="code">
            <ac:parameter ac:name="language">python</ac:parameter>
            <ac:parameter ac:name="breakoutMode">default</ac:parameter>
            <ac:parameter ac:name="breakoutWidth">full-width</ac:parameter>
            <ac:plain-text-body>print("test")</ac:plain-text-body>
        </ac:structured-macro>
        """
        doc2 = parser.parse(content2)
        codes = doc2.find_all(CodeMacro)
        assert len(codes) == 1
        assert codes[0].language == "python"
        assert codes[0].breakout_mode == "default"
        assert codes[0].breakout_width == "full-width"

    def test_jira_macro_parsing_all_params(self):
        """Test JIRA macro parsing with all parameters."""
        parser = ConfluenceParser()
        content = """
        <ac:structured-macro ac:name="jira">
            <ac:parameter ac:name="key">PROJ-123</ac:parameter>
            <ac:parameter ac:name="serverId">server-1</ac:parameter>
            <ac:parameter ac:name="server">Custom Server</ac:parameter>
        </ac:structured-macro>
        """
        doc = parser.parse(content)
        jiras = doc.find_all(JiraMacro)
        assert len(jiras) == 1
        jira = jiras[0]
        assert jira.key == "PROJ-123"
        assert jira.server_id == "server-1"
        assert jira.server == "Custom Server"

    def test_include_macro_parsing(self):
        """Test include macro parsing with resource identifiers including version_at_save."""
        parser = ConfluenceParser()
        content = """
        <ac:structured-macro ac:name="include">
            <ac:parameter ac:name="">
                <ri:page ri:space-key="TEST" ri:content-title="Include Page" ri:version-at-save="1"/>
            </ac:parameter>
        </ac:structured-macro>
        """
        doc = parser.parse(content)
        includes = doc.find_all(IncludeMacro)
        assert len(includes) == 1
        include = includes[0]
        assert include.space_key == "TEST"
        assert include.content_title == "Include Page"
        assert include.version_at_save == "1"  # Now this should work!

        # Check that resource identifiers are parsed correctly
        resources = doc.find_all(ResourceIdentifier)
        assert len(resources) >= 1
        resource = resources[0]
        assert resource.version_at_save == "1"

    def test_tasks_report_macro_parsing(self):
        """Test tasks report macro parameter parsing."""
        parser = ConfluenceParser()
        content = """
        <ac:structured-macro ac:name="tasks-report-macro">
            <ac:parameter ac:name="spaces">SPACE1,SPACE2</ac:parameter>
            <ac:parameter ac:name="isMissingRequiredParameters">true</ac:parameter>
        </ac:structured-macro>
        """
        doc = parser.parse(content)
        tasks = doc.find_all(TasksReportMacro)
        assert len(tasks) == 1
        task = tasks[0]
        assert task.spaces == "SPACE1,SPACE2"
        assert task.is_missing_required_parameters is True

    def test_excerpt_include_macro_parsing(self):
        """Test excerpt include macro parsing with version_at_save."""
        parser = ConfluenceParser()
        content = """
        <ac:structured-macro ac:name="excerpt-include">
            <ac:parameter ac:name="">
                <ri:blog-post ri:space-key="BLOG" ri:content-title="Blog Post" ri:posting-day="2023-01-01" ri:version-at-save="2"/>
            </ac:parameter>
        </ac:structured-macro>
        """
        doc = parser.parse(content)
        excerpts = doc.find_all(ExcerptIncludeMacro)
        assert len(excerpts) == 1
        excerpt = excerpts[0]
        assert excerpt.space_key == "BLOG"
        assert excerpt.content_title == "Blog Post"
        assert excerpt.posting_day == "2023-01-01"
        assert excerpt.version_at_save == "2"  # Now this should work!

        # Check that resource identifiers are parsed
        resources = doc.find_all(ResourceIdentifier)
        assert len(resources) >= 1
        resource = resources[0]
        assert resource.version_at_save == "2"

    def test_profile_macro_parsing(self):
        """Test profile macro parsing."""
        parser = ConfluenceParser()
        content = """
        <ac:structured-macro ac:name="profile">
            <ac:parameter ac:name="user">
                <ri:user ri:account-id="user123"/>
            </ac:parameter>
        </ac:structured-macro>
        """
        doc = parser.parse(content)
        profiles = doc.find_all(ProfileMacro)
        assert len(profiles) == 1
        profile = profiles[0]
        assert profile.account_id == "user123"

    def test_anchor_macro_parsing(self):
        """Test anchor macro parsing."""
        parser = ConfluenceParser()
        content = """
        <ac:structured-macro ac:name="anchor">
            <ac:parameter ac:name="">anchor-name</ac:parameter>
        </ac:structured-macro>
        """
        doc = parser.parse(content)
        anchors = doc.find_all(AnchorMacro)
        assert len(anchors) == 1
        anchor = anchors[0]
        assert anchor.anchor_name == "anchor-name"

    def test_excerpt_macro_with_rich_text(self):
        """Test excerpt macro parsing with rich text body."""
        parser = ConfluenceParser()
        content = """
        <ac:macro ac:name="excerpt">
            <ac:rich-text-body>
                <p>This is excerpt content</p>
                <strong>Bold text in excerpt</strong>
            </ac:rich-text-body>
        </ac:macro>
        """
        doc = parser.parse(content)
        excerpts = doc.find_all(ExcerptMacro)
        assert len(excerpts) == 1
        excerpt = excerpts[0]
        assert len(excerpt.children) > 0
        text = excerpt.to_text()
        assert "This is excerpt content" in text

    def test_external_link_mailto(self):
        """Test parsing external mailto links."""
        parser = ConfluenceParser()
        content = '<a href="mailto:test@example.com">Email Link</a>'
        doc = parser.parse(content)
        links = doc.find_all(LinkElement)
        assert len(links) == 1
        assert links[0].type == LinkType.MAILTO
        assert links[0].href == "mailto:test@example.com"

    def test_external_link_regular(self):
        """Test parsing regular external links."""
        parser = ConfluenceParser()
        content = '<a href="https://example.com">Web Link</a>'
        doc = parser.parse(content)
        links = doc.find_all(LinkElement)
        assert len(links) == 1
        assert links[0].type == LinkType.EXTERNAL
        assert links[0].href == "https://example.com"

    def test_link_body_parsing(self):
        """Test link body parsing as fragment."""
        parser = ConfluenceParser()
        content = """
        <ac:link>
            <ac:link-body>
                <p>Link content</p>
                <strong>Bold text</strong>
            </ac:link-body>
        </ac:link>
        """
        doc = parser.parse(content)
        fragments = doc.find_all(Fragment)
        # Link body should create fragments for rich content
        assert len(fragments) >= 1

    def test_image_url_parsing(self):
        """Test image parsing with URL element."""
        parser = ConfluenceParser()
        content = """
        <ac:image>
            <ri:url ri:value="https://example.com/test.jpg"/>
        </ac:image>
        """
        doc = parser.parse(content)
        images = doc.find_all(Image)
        assert len(images) == 1
        assert images[0].url_value == "https://example.com/test.jpg"

    def test_image_caption_parsing(self):
        """Test image parsing with caption element."""
        parser = ConfluenceParser()
        content = """
        <ac:image>
            <ac:caption>Image caption text</ac:caption>
        </ac:image>
        """
        doc = parser.parse(content)
        images = doc.find_all(Image)
        assert len(images) == 1
        assert len(images[0].children) > 0

    def test_image_attachment_parsing(self):
        """Test image parsing with attachment element."""
        parser = ConfluenceParser()
        content = """
        <ac:image>
            <ri:attachment ri:filename="test-image.png" ri:version-at-save="2"/>
        </ac:image>
        """
        doc = parser.parse(content)
        images = doc.find_all(Image)
        assert len(images) == 1
        assert images[0].filename == "test-image.png"
        assert images[0].version_at_save == "2"


if __name__ == "__main__":
    pytest.main([__file__])
