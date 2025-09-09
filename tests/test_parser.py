"""Tests for the Confluence content parser."""

from confluence_content_parser import ConfluenceParser
from confluence_content_parser.models import ConfluenceDocument


class TestConfluenceParser:
    """Test cases for ConfluenceParser."""

    def setup_method(self):
        """Set up test fixtures."""
        self.parser = ConfluenceParser()

    def test_parse_simple_paragraph(self):
        """Test parsing a simple paragraph."""
        content = "<p>Simple paragraph text</p>"
        document = self.parser.parse(content)

        assert isinstance(document, ConfluenceDocument)
        assert len(document.content) == 1
        assert document.content[0].type == "p"
        assert document.content[0].text == "Simple paragraph text"

    def test_parse_layout_structure(self):
        """Test parsing layout structures."""
        content = '''
        <ac:layout>
            <ac:layout-section ac:type="fixed-width">
                <ac:layout-cell>
                    <p>Cell content</p>
                </ac:layout-cell>
            </ac:layout-section>
        </ac:layout>
        '''
        document = self.parser.parse(content)

        assert len(document.content) == 1
        assert document.content[0].type == "layout"
        assert len(document.content[0].children) == 1
        layout_section = document.content[0].children[0]
        assert layout_section.type == "layout_section"
        assert layout_section.layout_section.type == "fixed-width"

    def test_parse_structured_macro(self):
        """Test parsing structured macros."""
        content = '''
        <ac:structured-macro ac:name="code" ac:macro-id="test-123">
            <ac:parameter ac:name="language">py</ac:parameter>
            <ac:plain-text-body><![CDATA[def test(): return None]]></ac:plain-text-body>
        </ac:structured-macro>
        '''
        document = self.parser.parse(content)

        assert len(document.content) == 1
        macro_element = document.content[0]
        assert macro_element.type == "code_block"
        assert macro_element.code_block.language == "py"
        assert "def test(): return None" in macro_element.code_block.content

    def test_parse_link_with_user_reference(self):
        """Test parsing links with user references."""
        content = '''
        <ac:link>
            <ri:user ri:account-id="123456" ri:local-id="user-local-id"/>
        </ac:link>
        '''
        document = self.parser.parse(content)

        assert len(document.content) == 1
        link_element = document.content[0]
        assert link_element.type == "link"
        assert link_element.link.user_reference is not None
        assert link_element.link.user_reference.account_id == "123456"
        assert link_element.link.user_reference.local_id == "user-local-id"

    def test_parse_table(self):
        """Test parsing table structures."""
        content = '''
        <table>
            <tbody>
                <tr>
                    <th>Header 1</th>
                    <th>Header 2</th>
                </tr>
                <tr>
                    <td>Cell 1</td>
                    <td>Cell 2</td>
                </tr>
            </tbody>
        </table>
        '''
        document = self.parser.parse(content)

        assert len(document.content) == 1
        table_element = document.content[0]
        assert table_element.type == "table"
        assert len(table_element.table.cells) == 2
        header_texts = []
        for cell in table_element.table.cells[0]:
            header_texts.append(" ".join((child.text or child.text_normalized()) for child in cell).strip())
        assert header_texts == ["Header 1", "Header 2"]
        body_texts = []
        for cell in table_element.table.cells[1]:
            body_texts.append(" ".join((child.text or child.text_normalized()) for child in cell).strip())
        assert body_texts == ["Cell 1", "Cell 2"]

    def test_parse_status_macro(self):
        """Test parsing status macros."""
        content = '''
        <ac:structured-macro ac:name="status" ac:macro-id="status-123">
            <ac:parameter ac:name="title">In Progress</ac:parameter>
            <ac:parameter ac:name="colour">Blue</ac:parameter>
        </ac:structured-macro>
        '''
        document = self.parser.parse(content)

        assert len(document.content) == 1
        status_element = document.content[0]
        assert status_element.type == "status"
        assert status_element.status.title == "In Progress"
        assert status_element.status.colour == "Blue"

    def test_parse_emoticon(self):
        """Test parsing emoticons."""
        content = '''
        <ac:emoticon ac:name="smile" ac:emoji-shortname=":smile:" ac:emoji-id="1f600" ac:emoji-fallback="😀"/>
        '''
        document = self.parser.parse(content)

        assert len(document.content) == 1
        emoticon_element = document.content[0]
        assert emoticon_element.type == "emoticon"
        assert emoticon_element.emoticon.name == "smile"
        assert emoticon_element.emoticon.emoji_shortname == ":smile:"

    def test_parse_date_element(self):
        """Test parsing date elements."""
        content = '<time datetime="2025-09-24"/>'
        document = self.parser.parse(content)

        assert len(document.content) == 1
        date_element = document.content[0]
        assert date_element.type == "date"
        assert date_element.date.datetime == "2025-09-24"

    def test_parse_anchor_link(self):
        """Test parsing regular anchor links."""
        content = '<a href="https://example.com" data-card-appearance="inline">Example Link</a>'
        document = self.parser.parse(content)

        assert len(document.content) == 1
        link_element = document.content[0]
        assert link_element.type == "link"
        assert link_element.link.url == "https://example.com"
        assert link_element.link.text == "Example Link"
        assert link_element.link.card_appearance == "inline"

    def test_parse_complex_confluence_content(self):
        """Test parsing the complex example content provided."""
        content = '''
        <ac:layout>
            <ac:layout-section ac:type="fixed-width" ac:breakout-mode="default">
                <ac:layout-cell>
                    <p>I'm a 8+ years Machine Learning Engineer building AI agents in production.</p>
                    <p>When I first started, I made the same mistake most people do: I focused on getting a flashy demo instead of building something that could survive real-world production.</p>
                    <p>It worked fine at first. <ac:link><ri:user ri:account-id="70121:62d04f60-2553-48fa-91c0-e24b33a36038" ri:local-id="8eac8daa-37ff-44cc-b45b-6b7d6daeaa1a" /></ac:link> The prototype looked smart, responded fast, and used the latest open-source libraries. But the minute it hit a real user environment, things fell apart.</p>
                </ac:layout-cell>
            </ac:layout-section>
        </ac:layout>
        '''
        document = self.parser.parse(content)

        assert isinstance(document, ConfluenceDocument)
        assert len(document.content) == 1
        assert document.content[0].type == "layout"

        # Navigate through the structure
        layout_section = document.content[0].children[0]
        assert layout_section.type == "layout_section"
        assert layout_section.layout_section.type == "fixed-width"
        assert layout_section.layout_section.breakout_mode == "default"

        # Check that we have the paragraphs and user link
        layout_cell = layout_section.layout_section.cells[0]
        assert len(layout_cell.content) == 3  # Three paragraphs

        # Check the third paragraph contains the user link
        third_paragraph = layout_cell.content[2]
        assert third_paragraph.type == "p"
        # The user link should be in the children
        user_links = [child for child in third_paragraph.children if child.type == "link" and child.link.user_reference]
        assert len(user_links) == 1
        assert user_links[0].link.user_reference.account_id == "70121:62d04f60-2553-48fa-91c0-e24b33a36038"

    def test_empty_content(self):
        """Test parsing empty content."""
        document = self.parser.parse("<div></div>")
        assert isinstance(document, ConfluenceDocument)
        assert len(document.content) == 1
        assert document.content[0].type == "div"

    def test_malformed_xml_fallback_to_html(self):
        """Test that malformed XML falls back to HTML parsing."""
        content = "<p>Unclosed paragraph"
        document = self.parser.parse(content)
        assert isinstance(document, ConfluenceDocument)
        # Should still parse as HTML
        assert len(document.content) > 0

    def test_parse_panel_macro(self):
        """Test parsing panel macros."""
        content = '''
        <ac:structured-macro ac:name="panel" ac:macro-id="panel-123">
            <ac:parameter ac:name="title">Important Note</ac:parameter>
            <ac:parameter ac:name="borderStyle">solid</ac:parameter>
            <ac:parameter ac:name="borderColor">#0052CC</ac:parameter>
            <ac:parameter ac:name="titleBGColor">#E6FCFF</ac:parameter>
            <ac:parameter ac:name="titleColor">#0052CC</ac:parameter>
            <ac:parameter ac:name="bgColor">#F4F9FF</ac:parameter>
            <ac:parameter ac:name="panelIcon">:rainbow:</ac:parameter>
            <ac:parameter ac:name="panelIconId">1f308</ac:parameter>
            <ac:parameter ac:name="panelIconText">🌈</ac:parameter>
            <ac:rich-text-body>
                <p>This is an important message in a panel.</p>
            </ac:rich-text-body>
        </ac:structured-macro>
        '''
        document = self.parser.parse(content)

        assert len(document.content) == 1
        panel_element = document.content[0]
        assert panel_element.type == "panel"
        assert panel_element.panel.title == "Important Note"
        assert panel_element.panel.border_style == "solid"
        assert panel_element.panel.border_color == "#0052CC"
        assert panel_element.panel.title_bg_color == "#E6FCFF"
        assert panel_element.panel.title_color == "#0052CC"
        assert panel_element.panel.bg_color == "#F4F9FF"
        assert "This is an important message in a panel." in panel_element.panel.content
        assert panel_element.panel.icon == ":rainbow:"
        assert panel_element.panel.icon_id == "1f308"
        assert panel_element.panel.icon_text == "🌈"
        assert any(child.type == "p" for child in panel_element.panel.children)

    def test_parse_task_element(self):
        """Test parsing ac:task elements."""
        content = '''
        <ac:task ac:local-id="task-001" ac:task-id="123456" status="complete">
            <ac:task-status>complete</ac:task-status>
            <ac:task-body>Complete the documentation</ac:task-body>
        </ac:task>
        '''
        document = self.parser.parse(content)

        assert len(document.content) == 1
        task_element = document.content[0]
        assert task_element.type == "task"
        assert task_element.task.local_id == "task-001"
        assert task_element.task.task_id == "123456"
        assert task_element.task.status == "complete"
        assert "Complete the documentation" in task_element.task.body

    def test_parse_i18n_element(self):
        """Test parsing at:i18n elements."""
        content = '''
        <at:i18n at:key="confluence.page.title.example"/>
        '''
        document = self.parser.parse(content)

        assert len(document.content) == 1
        i18n_element = document.content[0]
        assert i18n_element.type == "i18n"
        assert i18n_element.i18n.key == "confluence.page.title.example"

    def test_parse_adf_extension(self):
        """Test parsing ac:adf-extension elements."""
        content = '''
        <ac:adf-extension extension-type="com.atlassian.confluence.macro.core" extension-key="expand">
            <ac:parameter ac:name="title">Click to expand</ac:parameter>
            <ac:content>
                <p>Hidden content that expands</p>
            </ac:content>
        </ac:adf-extension>
        '''
        document = self.parser.parse(content)

        # The parser emits the adf_extension and also nested content nodes.
        adf_elements = [el for el in document.content if el.type == "adf_extension"]
        assert len(adf_elements) == 1
        adf_element = adf_elements[0]
        assert adf_element.adf_extension.extension_type == "com.atlassian.confluence.macro.core"
        assert adf_element.adf_extension.extension_key == "expand"
        assert adf_element.adf_extension.parameters["title"] == "Click to expand"
        assert "Hidden content that expands" in adf_element.adf_extension.content

    def test_parse_adf_extension_with_decision_list_fallback(self):
        """ADF decision-list inside extension should materialize DecisionList via fallback."""
        content = '''
        <ac:adf-extension>
          <ac:adf-node type="decision-list" local-id="dec-1">
            <ac:adf-attribute key="state">DECIDED</ac:adf-attribute>
          </ac:adf-node>
          <ac:adf-fallback>
            <ul class="decision-list"><li>Decision</li></ul>
          </ac:adf-fallback>
        </ac:adf-extension>
        '''
        document = self.parser.parse(content)

        types = [el.type for el in document.content]
        assert "adf_extension" in types
        assert "decision_list" in types
        decision_el = next(el for el in document.content if el.type == "decision_list")
        assert decision_el.decision_list.local_id == "dec-1"
        assert len(decision_el.decision_list.items) == 1
        assert decision_el.decision_list.items[0].content == "Decision"

    def test_parse_placeholder(self):
        """Test parsing ac:placeholder elements."""
        content = '''
        <ac:placeholder ac:type="mention">@username</ac:placeholder>
        '''
        document = self.parser.parse(content)

        assert len(document.content) == 1
        placeholder_element = document.content[0]
        assert placeholder_element.type == "placeholder"
        assert placeholder_element.placeholder.type == "mention"
        assert placeholder_element.placeholder.text == "@username"

    def test_parse_inline_comment(self):
        """Test parsing ac:inline-comment-marker elements."""
        content = '''
        <ac:inline-comment-marker ac:ref="comment-123">Highlighted text</ac:inline-comment-marker>
        '''
        document = self.parser.parse(content)

        assert len(document.content) == 1
        comment_element = document.content[0]
        assert comment_element.type == "inline_comment"
        assert comment_element.inline_comment.ref == "comment-123"
        assert comment_element.inline_comment.text == "Highlighted text"

    def test_parse_image_with_attachment(self):
        """Test parsing ac:image with attachment reference."""
        content = '''
        <ac:image ac:alt="Screenshot" ac:title="Example Screenshot" ac:width="500" ac:height="300">
            <ri:attachment ri:filename="screenshot.png" ri:content-id="12345" ri:version-at-save="1"/>
        </ac:image>
        '''
        document = self.parser.parse(content)

        assert len(document.content) == 1
        image_element = document.content[0]
        assert image_element.type == "image"
        assert image_element.image.alt == "Screenshot"
        assert image_element.image.title == "Example Screenshot"
        assert image_element.image.width == "500"
        assert image_element.image.height == "300"
        assert image_element.image.attachment_reference is not None
        assert image_element.image.attachment_reference.filename == "screenshot.png"
        assert image_element.image.attachment_reference.content_id == "12345"

    def test_parse_image_with_url(self):
        """Test parsing ac:image with URL reference."""
        content = '''
        <ac:image ac:alt="External image">
            <ri:url ri:value="https://example.com/image.png"/>
        </ac:image>
        '''
        document = self.parser.parse(content)

        assert len(document.content) == 1
        image_element = document.content[0]
        assert image_element.type == "image"
        assert image_element.image.alt == "External image"
        assert image_element.image.url_reference is not None
        assert image_element.image.url_reference.value == "https://example.com/image.png"

    def test_parse_task_list_macro(self):
        """Test parsing task-list macros with multiple items."""
        content = '''
        <ac:structured-macro ac:name="task-list" ac:macro-id="tasklist-123">
            <ac:task-item ac:local-id="item-1" ac:task-id="task-1" completed="false">
                Buy groceries
            </ac:task-item>
            <ac:task-item ac:local-id="item-2" ac:task-id="task-2" completed="true">
                Walk the dog
            </ac:task-item>
        </ac:structured-macro>
        '''
        document = self.parser.parse(content)

        assert len(document.content) == 1
        task_list_element = document.content[0]
        assert task_list_element.type == "task_list"
        assert task_list_element.task_list.local_id == "tasklist-123"
        assert len(task_list_element.task_list.items) == 2

        first_item = task_list_element.task_list.items[0]
        assert first_item.local_id == "item-1"
        assert first_item.task_id == "task-1"
        assert first_item.completed is False
        assert "Buy groceries" in first_item.content

        second_item = task_list_element.task_list.items[1]
        assert second_item.local_id == "item-2"
        assert second_item.task_id == "task-2"
        assert second_item.completed is True
        assert "Walk the dog" in second_item.content

    def test_parse_complex_nested_content(self):
        """Test parsing complex nested content with new elements."""
        content = '''
        <ac:layout>
            <ac:layout-section ac:type="two-column">
                <ac:layout-cell>
                    <ac:structured-macro ac:name="panel" ac:macro-id="panel-456">
                        <ac:parameter ac:name="title">Status Panel</ac:parameter>
                        <ac:rich-text-body>
                            <p>Current status: <ac:structured-macro ac:name="status" ac:macro-id="status-456">
                                <ac:parameter ac:name="title">Active</ac:parameter>
                                <ac:parameter ac:name="colour">Green</ac:parameter>
                            </ac:structured-macro></p>
                        </ac:rich-text-body>
                    </ac:structured-macro>
                </ac:layout-cell>
                <ac:layout-cell>
                    <ac:task ac:local-id="task-002" ac:task-id="789" status="incomplete">
                        Review the panel content
                    </ac:task>
                </ac:layout-cell>
            </ac:layout-section>
        </ac:layout>
        '''
        document = self.parser.parse(content)

        assert len(document.content) == 1
        layout = document.content[0]
        assert layout.type == "layout"

        # Check the layout section
        layout_section = layout.children[0]
        assert layout_section.type == "layout_section"
        assert layout_section.layout_section.type == "two-column"
        assert len(layout_section.layout_section.cells) == 2

        # Check first cell has panel
        first_cell_content = layout_section.layout_section.cells[0].content
        panel_element = first_cell_content[0]
        assert panel_element.type == "panel"
        assert panel_element.panel.title == "Status Panel"

        # Check second cell has task
        second_cell_content = layout_section.layout_section.cells[1].content
        task_element = second_cell_content[0]
        assert task_element.type == "task"
        assert task_element.task.local_id == "task-002"
        assert task_element.task.status == "incomplete"

    def test_parse_notification_macros(self):
        """Test parsing info, warning, note, tip macros."""
        content = '''
        <ac:structured-macro ac:name="info" ac:macro-id="info-123">
            <ac:rich-text-body>
                <p>This is an info message.</p>
            </ac:rich-text-body>
        </ac:structured-macro>
        '''
        document = self.parser.parse(content)

        assert len(document.content) == 1
        info_element = document.content[0]
        assert info_element.type == "notification_macro"
        assert info_element.notification_macro.macro_type == "info"
        assert "This is an info message." in info_element.notification_macro.content

    def test_parse_view_file_macro(self):
        """Test parsing view-file macros."""
        content = '''
        <ac:structured-macro ac:name="view-file" ac:macro-id="viewfile-123">
            <ac:parameter ac:name="name">document.pdf</ac:parameter>
            <ac:parameter ac:name="version-at-save">2</ac:parameter>
        </ac:structured-macro>
        '''
        document = self.parser.parse(content)

        assert len(document.content) == 1
        view_file_element = document.content[0]
        assert view_file_element.type == "view_file_macro"
        assert view_file_element.view_file_macro.name == "document.pdf"
        assert view_file_element.view_file_macro.version_at_save == "2"

    def test_parse_view_file_macro_with_attachment_parameter(self):
        """Test parsing view-file macro when 'name' parameter contains an attachment node."""
        content = '''
        <ac:structured-macro ac:name="view-file" ac:macro-id="viewfile-456">
            <ac:parameter ac:name="name"><ri:attachment ri:filename="PDF Guideline.pdf" ri:version-at-save="1"/></ac:parameter>
        </ac:structured-macro>
        '''
        document = self.parser.parse(content)

        assert len(document.content) == 1
        view_file_element = document.content[0]
        assert view_file_element.type == "view_file_macro"
        assert view_file_element.view_file_macro.attachment_filename == "PDF Guideline.pdf"
        assert view_file_element.view_file_macro.attachment_version_at_save == "1"

    def test_parse_gadget_macro(self):
        """Test parsing gadget macros."""
        content = '''
        <ac:structured-macro ac:name="gadget" ac:local-id="gadget-123" data-layout="default">
            <ac:parameter ac:name="url">https://example.com/gadget.xml</ac:parameter>
        </ac:structured-macro>
        '''
        document = self.parser.parse(content)

        assert len(document.content) == 1
        gadget_element = document.content[0]
        assert gadget_element.type == "gadget_macro"
        assert gadget_element.gadget_macro.url == "https://example.com/gadget.xml"
        assert gadget_element.gadget_macro.local_id == "gadget-123"

    def test_parse_expand_macro(self):
        """Test parsing expand macros."""
        content = '''
        <ac:structured-macro ac:name="expand" ac:macro-id="expand-123">
            <ac:parameter ac:name="title">Click to expand</ac:parameter>
            <ac:parameter ac:name="breakoutWidth">760</ac:parameter>
            <ac:rich-text-body>
                <p>Hidden expandable content here.</p>
            </ac:rich-text-body>
        </ac:structured-macro>
        '''
        document = self.parser.parse(content)

        assert len(document.content) == 1
        expand_element = document.content[0]
        assert expand_element.type == "expand_macro"
        assert expand_element.expand_macro.title == "Click to expand"
        assert expand_element.expand_macro.breakout_width == "760"
        assert "Hidden expandable content here." in expand_element.expand_macro.content
        assert any(child.type == "p" for child in expand_element.expand_macro.children)

    def test_parse_toc_macro(self):
        """Test parsing table of contents macros."""
        content = '''
        <ac:structured-macro ac:name="toc" ac:local-id="toc-123">
            <ac:parameter ac:name="style">disc</ac:parameter>
        </ac:structured-macro>
        '''
        document = self.parser.parse(content)

        assert len(document.content) == 1
        toc_element = document.content[0]
        assert toc_element.type == "toc_macro"
        assert toc_element.toc_macro.style == "disc"
        assert toc_element.toc_macro.local_id == "toc-123"

        # identities and kinds exist on elements
        assert toc_element.id is not None
        assert isinstance(toc_element.path, list)
        assert toc_element.kind is not None

    def test_parse_new_common_macros(self):
        # excerpt
        content = '''
        <ac:structured-macro ac:name="excerpt" ac:macro-id="ex-1">
            <ac:parameter ac:name="hidden">true</ac:parameter>
            <ac:rich-text-body><p>Excerpt body</p></ac:rich-text-body>
        </ac:structured-macro>
        '''
        document = self.parser.parse(content)
        assert len(document.content) == 1
        assert document.content[0].type in {"excerpt_macro", "macro"}
        if document.content[0].type == "excerpt_macro":
            ex = document.content[0].excerpt_macro
            assert ex is not None
            assert any(child.type == "p" for child in ex.children)

        # excerpt-include
        content = '''
        <ac:structured-macro ac:name="excerpt-include" ac:macro-id="exi-1">
            <ac:parameter ac:name="page">Home</ac:parameter>
        </ac:structured-macro>
        '''
        document = self.parser.parse(content)
        assert len(document.content) == 1
        assert document.content[0].type in {"excerpt_include_macro", "macro"}

        # page-properties
        content = '''
        <ac:structured-macro ac:name="page-properties" ac:macro-id="pp-1">
            <ac:parameter ac:name="hidden">false</ac:parameter>
            <ac:rich-text-body><p>Table</p></ac:rich-text-body>
        </ac:structured-macro>
        '''
        document = self.parser.parse(content)
        assert len(document.content) == 1
        assert document.content[0].type in {"page_properties_macro", "macro"}
        if document.content[0].type == "page_properties_macro":
            ppm = document.content[0].page_properties_macro
            assert ppm is not None
            assert any(child.type == "p" for child in ppm.children)

        # page-properties-report
        content = '''
        <ac:structured-macro ac:name="page-properties-report" ac:macro-id="ppr-1">
            <ac:parameter ac:name="labels">k1,k2</ac:parameter>
            <ac:parameter ac:name="spaceKey">FOO</ac:parameter>
        </ac:structured-macro>
        '''
        document = self.parser.parse(content)
        assert len(document.content) == 1
        assert document.content[0].type in {"page_properties_report_macro", "macro"}

        # children-display
        content = '''
        <ac:structured-macro ac:name="children-display" ac:macro-id="cd-1">
            <ac:parameter ac:name="depth">2</ac:parameter>
            <ac:parameter ac:name="excerpt">simple</ac:parameter>
            <ac:parameter ac:name="sort">creation</ac:parameter>
            <ac:parameter ac:name="reverse">true</ac:parameter>
        </ac:structured-macro>
        '''
        document = self.parser.parse(content)
        assert len(document.content) == 1
        assert document.content[0].type in {"children_display_macro", "macro"}

        # attachments
        content = '''
        <ac:structured-macro ac:name="attachments" ac:macro-id="att-1">
            <ac:parameter ac:name="patterns">*.png,*.jpg</ac:parameter>
        </ac:structured-macro>
        '''
        document = self.parser.parse(content)
        assert len(document.content) == 1
        assert document.content[0].type in {"attachments_macro", "macro"}

    def test_parse_enhanced_jira_macro(self):
        """Test parsing enhanced jira macros."""
        content = '''
        <ac:structured-macro ac:name="jira" ac:macro-id="jira-123">
            <ac:parameter ac:name="key">PROJ-123</ac:parameter>
            <ac:parameter ac:name="serverId">server-456</ac:parameter>
            <ac:parameter ac:name="server">Production Jira</ac:parameter>
        </ac:structured-macro>
        '''
        document = self.parser.parse(content)

        assert len(document.content) == 1
        jira_element = document.content[0]
        assert jira_element.type == "jira_macro"
        assert jira_element.jira_macro.key == "PROJ-123"
        assert jira_element.jira_macro.server_id == "server-456"
        assert jira_element.jira_macro.server == "Production Jira"

    def test_parse_task_list_container(self):
        """Test parsing direct ac:task-list containers (different from macro task lists)."""
        content = '''
        <ac:task-list>
            <ac:task>
                <ac:task-id>task-001</ac:task-id>
                <ac:task-uuid>uuid-001</ac:task-uuid>
                <ac:task-status>complete</ac:task-status>
                <ac:task-body>Task description here</ac:task-body>
            </ac:task>
            <ac:task>
                <ac:task-id>task-002</ac:task-id>
                <ac:task-uuid>uuid-002</ac:task-uuid>
                <ac:task-status>incomplete</ac:task-status>
                <ac:task-body>Another task</ac:task-body>
            </ac:task>
        </ac:task-list>
        '''
        document = self.parser.parse(content)

        assert len(document.content) == 1
        task_container = document.content[0]
        assert task_container.type == "task_list_container"
        assert len(task_container.task_list_container.tasks) == 2

        first_task = task_container.task_list_container.tasks[0]
        assert first_task.task_id == "task-001"
        assert first_task.task_uuid == "uuid-001"
        assert first_task.status == "complete"
        assert first_task.body == "Task description here"

        second_task = task_container.task_list_container.tasks[1]
        assert second_task.task_id == "task-002"
        assert second_task.status == "incomplete"

    def test_parse_horizontal_rule(self):
        """Test parsing horizontal rules."""
        content = '<hr />'
        document = self.parser.parse(content)

        assert len(document.content) == 1
        hr_element = document.content[0]
        assert hr_element.type == "hr"

    def test_parse_enhanced_code_block(self):
        """Test parsing code blocks with breakout parameters."""
        content = '''
        <ac:structured-macro ac:name="code" ac:macro-id="code-123">
            <ac:parameter ac:name="language">python</ac:parameter>
            <ac:parameter ac:name="title">Example Code</ac:parameter>
            <ac:parameter ac:name="breakoutMode">wide</ac:parameter>
            <ac:parameter ac:name="breakoutWidth">1200</ac:parameter>
            <ac:plain-text-body><![CDATA[
def hello():
    return "Hello World"
            ]]></ac:plain-text-body>
        </ac:structured-macro>
        '''
        document = self.parser.parse(content)

        assert len(document.content) == 1
        code_element = document.content[0]
        assert code_element.type == "code_block"
        assert code_element.code_block.language == "python"
        assert code_element.code_block.title == "Example Code"
        assert code_element.code_block.breakout_mode == "wide"
        assert code_element.code_block.breakout_width == "1200"
        assert "def hello():" in code_element.code_block.content

    def test_parse_advanced_content_sample(self):
        """Test parsing a subset of the advanced content provided by the user."""
        content = '''
        <ac:layout>
            <ac:layout-section ac:type="fixed-width">
                <ac:layout-cell>
                    <h2>Advanced Features</h2>
                    <ac:task-list>
                        <ac:task>
                            <ac:task-id>1</ac:task-id>
                            <ac:task-status>incomplete</ac:task-status>
                            <ac:task-body>Sample task</ac:task-body>
                        </ac:task>
                    </ac:task-list>
                    <ac:structured-macro ac:name="info">
                        <ac:rich-text-body><p>Information panel</p></ac:rich-text-body>
                    </ac:structured-macro>
                    <ac:structured-macro ac:name="jira">
                        <ac:parameter ac:name="key">TEST-123</ac:parameter>
                    </ac:structured-macro>
                    <hr />
                </ac:layout-cell>
            </ac:layout-section>
        </ac:layout>
        '''
        document = self.parser.parse(content)

        assert len(document.content) == 1
        layout = document.content[0]
        assert layout.type == "layout"
        assert layout.id is not None
        assert layout.kind is not None

        # Verify that the layout contains all the expected nested elements
        layout_section = layout.children[0]
        assert layout_section.type == "layout_section"
        # layout scope should be available for children inside cells
        cell_content = layout_section.layout_section.cells[0].content
        assert all(hasattr(el, "layout_scope") for el in cell_content)

        cell_content = layout_section.layout_section.cells[0].content

        # Check for heading
        h2_elements = [elem for elem in cell_content if elem.type == "h2"]
        assert len(h2_elements) == 1
        # heading scope for following siblings
        assert h2_elements[0].id is not None

        # Check for task list container
        task_containers = [elem for elem in cell_content if elem.type == "task_list_container"]
        assert len(task_containers) == 1
        assert len(task_containers[0].task_list_container.tasks) == 1

        # Check for notification macro
        info_macros = [elem for elem in cell_content if elem.type == "notification_macro"]
        assert len(info_macros) == 1
        assert info_macros[0].notification_macro.macro_type == "info"

        # Check for jira macro
        jira_macros = [elem for elem in cell_content if elem.type == "jira_macro"]
        assert len(jira_macros) == 1
        assert jira_macros[0].jira_macro.key == "TEST-123"

        # Check for horizontal rule
        hr_elements = [elem for elem in cell_content if elem.type == "hr"]
        assert len(hr_elements) == 1


    def test_parse_enhanced_image_attributes(self):
        """Test parsing images with enhanced attributes."""
        content = '''
        <ac:image ac:align="center" ac:layout="center" ac:original-height="1920"
                  ac:original-width="1080" ac:custom-width="true" ac:width="760">
            <ri:attachment ri:filename="screenshot.png" />
        </ac:image>
        '''
        document = self.parser.parse(content)

        assert len(document.content) == 1
        image_element = document.content[0]
        assert image_element.type == "image"
        assert image_element.image.alignment == "center"
        assert image_element.image.layout == "center"
        assert image_element.image.original_height == "1920"
        assert image_element.image.original_width == "1080"
        assert image_element.image.custom_width is True
        assert image_element.image.width == "760"

    def test_parse_text_formatting_elements(self):
        """Test parsing various text formatting elements."""
        content = '''
        <p>This has <strong>bold</strong>, <em>italic</em>, <u>underlined</u>,
           <del>deleted</del>, <sub>subscript</sub>, and <sup>superscript</sup> text.</p>
        '''
        document = self.parser.parse(content)

        assert len(document.content) == 1
        p_element = document.content[0]
        assert p_element.type == "p"

        # Check for different formatting elements in children
        formatting_types = {child.type for child in p_element.children}
        expected_types = {"strong", "em", "u", "del", "sub", "sup", "text"}
        assert expected_types.issubset(formatting_types)

    def test_parse_empty_and_self_closing_elements(self):
        """Test parsing empty paragraphs and self-closing elements."""
        content = '''<root><p /><hr /><br /></root>'''
        document = self.parser.parse(content)

        # The parser correctly parses each element separately
        assert len(document.content) == 3
        assert document.content[0].type == "p"
        assert document.content[1].type == "hr"
        assert document.content[2].type == "br"

    def test_parse_standalone_layout_cell(self):
        """Cover direct layout-cell branch and layout_cell parsing."""
        content = '''<ac:layout-cell><p>x</p></ac:layout-cell>'''
        document = self.parser.parse(content)

        assert len(document.content) == 1
        cell = document.content[0]
        assert cell.type == "layout_cell"
        assert len(cell.layout_cell.content) == 1
        assert cell.layout_cell.content[0].type == "p"
        assert cell.layout_cell.content[0].text == "x"

    def test_parse_generic_unknown_tag(self):
        """Cover generic element path for unknown tags."""
        content = '<foo><bar>text</bar></foo>'
        document = self.parser.parse(content)

        assert len(document.content) == 1
        foo = document.content[0]
        assert foo.type == "foo"
        assert foo.kind is None
        assert len(foo.children) == 1
        bar = foo.children[0]
        assert bar.type == "bar"
        assert bar.text == "text"
        assert bar.kind is None

    def test_parse_unknown_macro_falls_back_to_macro_element(self):
        """Cover default macro branch when name is unrecognized."""
        content = '''
        <ac:structured-macro ac:name="xyz" ac:macro-id="m-1">
            <ac:parameter ac:name="a">b</ac:parameter>
        </ac:structured-macro>
        '''
        document = self.parser.parse(content)

        assert len(document.content) == 1
        el = document.content[0]
        assert el.type == "macro"
        assert el.macro is not None
        assert el.macro.name == "xyz"
        assert el.macro.parameters["a"] == "b"

        # also cover a known branch just above default (e.g., toc), to ensure line 237 path was hit
        content = '''<ac:structured-macro ac:name="anchor" ac:macro-id="anc-1"/>'''
        document = self.parser.parse(content)
        # handler runs even without params
        assert len(document.content) == 1

    def test_parse_link_with_page_reference(self):
        """Cover page reference branch for ac:link."""
        content = '''
        <ac:link>
            <ri:page ri:content-title="Template - Decision documentation" ri:version-at-save="1" />
        </ac:link>
        '''
        document = self.parser.parse(content)

        assert len(document.content) == 1
        el = document.content[0]
        assert el.type == "link"
        assert el.link.page_reference is not None
        assert el.link.page_reference.content_title == "Template - Decision documentation"
        assert el.link.page_reference.version_at_save == 1

    def test_parse_link_with_attachment_and_body(self):
        """Cover attachment and link-body branches for ac:link."""
        content = '''
        <ac:link>
            <ri:attachment ri:filename="file.pdf" ri:version-at-save="3" />
            <ac:link-body>Attachment</ac:link-body>
        </ac:link>
        '''
        document = self.parser.parse(content)

        assert len(document.content) == 1
        el = document.content[0]
        assert el.type == "link"
        assert el.link.attachment_reference is not None
        assert el.link.attachment_reference.filename == "file.pdf"
        assert el.link.attachment_reference.version_at_save == 3
        assert el.link.text == "Attachment"

    def test_parse_link_with_url_reference(self):
        """Cover url reference branch for ac:link."""
        content = '''
        <ac:link>
            <ri:url ri:value="https://example.com" />
        </ac:link>
        '''
        document = self.parser.parse(content)

        assert len(document.content) == 1
        el = document.content[0]
        assert el.type == "link"
        assert el.link.url_reference is not None
        assert el.link.url_reference.value == "https://example.com"

    def test_parse_extended_link_identifiers_and_plain_text_body(self):
        """Cover blog-post, space, content-entity, shortcut, and plain-text body."""
        content = '''
        <ac:link>
            <ri:blog-post ri:space-key="FOO" ri:content-title="First Post" ri:posting-day="2012/01/30" />
            <ac:plain-text-link-body><![CDATA[Blog]]></ac:plain-text-link-body>
        </ac:link>
        '''
        document = self.parser.parse(content)
        assert len(document.content) == 1
        el = document.content[0]
        assert el.type == "link"
        assert el.link.blog_post_reference is not None
        assert el.link.blog_post_reference.space_key == "FOO"
        assert el.link.blog_post_reference.content_title == "First Post"
        assert el.link.blog_post_reference.posting_day == "2012/01/30"
        assert el.link.text == "Blog"

        content = '''
        <ac:link><ri:space ri:space-key="TST"/></ac:link>
        '''
        document = self.parser.parse(content)
        el = document.content[0]
        assert el.link.space_reference is not None
        assert el.link.space_reference.space_key == "TST"

        content = '''
        <ac:link><ri:content-entity ri:content-id="123"/></ac:link>
        '''
        document = self.parser.parse(content)
        el = document.content[0]
        assert el.link.content_entity_reference is not None
        assert el.link.content_entity_reference.content_id == "123"

        content = '''
        <ac:link><ri:shortcut ri:key="jira" ri:parameter="ABC-1"/></ac:link>
        '''
        document = self.parser.parse(content)
        el = document.content[0]
        assert el.link.shortcut_reference is not None
        assert el.link.shortcut_reference.key == "jira"
        assert el.link.shortcut_reference.parameter == "ABC-1"

    def test_parse_adf_node_default(self):
        """Cover default AdfNode creation and append path."""
        content = '''
        <ac:adf-node type="custom" local-id="l1">
          <ac:adf-attribute key="k">v</ac:adf-attribute>
          <ac:adf-content>hello</ac:adf-content>
        </ac:adf-node>
        '''
        document = self.parser.parse(content)

        assert len(document.content) == 1
        node_el = document.content[0]
        assert node_el.type == "adf_node"
        assert node_el.adf_node.type == "custom"
        assert node_el.adf_node.local_id == "l1"
        assert node_el.adf_node.attributes.get("k") == "v"
        assert node_el.adf_node.content == "hello"

    def test_parse_adf_node_with_nested_child_node(self):
        """Cover nested adf-node path to execute child_nodes recursion and extend logic."""
        content = '''
        <ac:adf-node type="container" local-id="c1">
          <ac:adf-node type="paragraph" local-id="p1">
            <ac:adf-content>text</ac:adf-content>
          </ac:adf-node>
        </ac:adf-node>
        '''
        document = self.parser.parse(content)

        assert len(document.content) == 1
        node_el = document.content[0]
        assert node_el.type == "adf_node"
        assert node_el.adf_node.type == "container"
        # ensure the code path executed (no assertion on children semantics)

    def test_parse_adf_node_decision_list_direct(self):
        """Cover direct decision-list mapping path without fallback."""
        content = '''
        <ac:adf-node type="decision-list" local-id="dec-2">
          <ac:adf-node type="decision-item" local-id="it-1">
            <ac:adf-content>Item</ac:adf-content>
          </ac:adf-node>
        </ac:adf-node>
        '''
        document = self.parser.parse(content)

        assert len(document.content) == 1
        dl = document.content[0]
        assert dl.type == "decision_list"
        assert dl.decision_list.local_id == "dec-2"
        # Items list may be empty without fallback li entries
        assert isinstance(dl.decision_list.items, list)
        # Access kind to cover property branch
        assert dl.kind == "decision_list"

    def test_parse_adf_node_decision_list_with_direct_li(self):
        """Cover li extraction inside decision-list branch to hit lines 813-815."""
        content = '''
        <ac:adf-node type="decision-list" local-id="dec-3">
          <ul class="decision-list"><li>Direct decision</li></ul>
        </ac:adf-node>
        '''
        document = self.parser.parse(content)

        assert len(document.content) == 1
        dl = document.content[0]
        assert dl.type == "decision_list"
        assert dl.decision_list.local_id == "dec-3"
        assert [it.content for it in dl.decision_list.items] == ["Direct decision"]

    def test_helpers_iteration_and_text_normalized(self):
        content = '''<p>This <strong>has</strong> tails</p>'''
        document = self.parser.parse(content)
        el = document.content[0]
        assert el.text_normalized() == "This has tails"
        # iter yields at least the parent and its children
        assert len(list(el.iter())) >= 2
        # find_all by type
        found = el.find_all(type="strong")
        assert len(found) == 1
        # id/path/kind assigned
        assert el.id is not None and isinstance(el.path, list)

    def test_link_canonical_uri_variants(self):
        content = '''
            <ac:link><ri:user ri:account-id="acc-1"/></ac:link>
            <ac:link><ri:page ri:space-key="FOO" ri:content-title="Bar"/></ac:link>
            <ac:link><ri:attachment ri:filename="file.pdf" ri:version-at-save="3"/></ac:link>
            <ac:link><ri:content-entity ri:content-id="123"/></ac:link>
            <ac:link><ri:shortcut ri:key="jira" ri:parameter="ABC-1"/></ac:link>
            <a href="https://e.com">x</a>
        '''
        document = self.parser.parse(content)
        links = [e for e in document.content if e.kind == "link"]
        uris = [e.link.canonical_uri for e in links]
        assert "user://acc-1" in uris
        assert "page://FOO/Bar" in uris
        assert "attach://file.pdf@v3" in uris
        assert "contentid://123" in uris
        assert "shortcut://jira/ABC-1" in uris
        assert any(u.startswith("https://e.com") for u in uris if isinstance(u, str))
        # internal flags
        kinds = [e.link.kind for e in links]
        assert set(kinds) >= {"user","page","attachment","content_entity","shortcut","url"}

    def test_list_and_layout_scopes(self):
        content = '''
        <ac:layout>
          <ac:layout-section ac:type="two_equal">
            <ac:layout-cell>
              <ul><li><p>A</p><ol><li><p>B</p></li></ol></li></ul>
            </ac:layout-cell>
            <ac:layout-cell>
              <p>C</p>
            </ac:layout-cell>
          </ac:layout-section>
        </ac:layout>
        '''
        document = self.parser.parse(content)
        layout = document.content[0]
        sec = layout.children[0]
        cell0 = sec.layout_section.cells[0].content
        p_a = next(e for e in cell0 if e.type == "ul").children[0].children[0]
        assert p_a.list_scope.get("depth") == 1
        p_b = next(e for e in cell0 if e.type == "ul").children[0].children[1].children[0]
        assert p_b.list_scope.get("depth") == 2
        cell1 = sec.layout_section.cells[1].content
        assert all("cell_index" in e.layout_scope for e in cell1)

    def test_unknown_macro_diagnostics(self):
        content = '''<ac:structured-macro ac:name="xyz"/>'''
        doc = self.parser.parse(content)
        diags = doc.metadata.get("diagnostics") or []
        assert any(d.startswith("unknown_macro:") for d in diags)

    def test_link_additional_kinds(self):
        content = '''
            <ac:link><ri:blog-post ri:space-key="FOO" ri:content-title="First Post" ri:posting-day="2012/01/30"/></ac:link>
            <ac:link><ri:space ri:space-key="TST"/></ac:link>
            <ac:link><ac:unknown/></ac:link>
        '''
        document = self.parser.parse(content)
        links = [e for e in document.content if e.type == "link"]
        uris = [e.link.canonical_uri for e in links]
        assert "blog://FOO/First Post@2012/01/30" in uris
        assert "space://TST" in uris
        # unknown child processed without error
        assert any(l.link.kind is None or l.link.kind in {"blog_post","space"} for l in links)

    def test_link_page_with_version_at_save(self):
        content = '''<ac:link><ri:page ri:space-key="FOO" ri:content-title="Bar" ri:version-at-save="7"/></ac:link>'''
        doc = self.parser.parse(content)
        link_el = doc.content[0]
        assert link_el.link.canonical_uri == "page://FOO/Bar@v7"

    def test_table_cells_child_parsing(self):
        content = '''
        <table>
          <tbody>
            <tr><th><p>H1</p></th><th><p>H2</p></th></tr>
            <tr><td><strong>A</strong></td><td><em>B</em></td></tr>
          </tbody>
        </table>
        '''
        doc = self.parser.parse(content)
        t = doc.content[0].table
        # ensure children in rich cells parsed via _parse_element
        assert any(c.type == "p" for c in t.cells[0][0])
        assert any(c.type == "strong" for c in t.cells[1][0])
        assert any(c.type == "em" for c in t.cells[1][1])

    def test_kind_property_branches(self):
        # heading
        doc = self.parser.parse('<h3>t</h3>')
        assert doc.content[0].kind == "heading"

        # list and list_item
        doc = self.parser.parse('<ul><li>i</li></ul>')
        assert doc.content[0].kind == "list"
        assert doc.content[0].children[0].kind == "list_item"

        # hr and br
        doc = self.parser.parse('<hr/>')
        assert doc.content[0].kind == "hr"
        doc = self.parser.parse('<br/>')
        assert doc.content[0].kind == "br"

        # paragraph
        doc = self.parser.parse('<p>x</p>')
        assert doc.content[0].kind == "paragraph"

        # link
        doc = self.parser.parse('<a href="https://e.com">x</a>')
        assert doc.content[0].kind == "link"

        # image
        doc = self.parser.parse('<ac:image><ri:url ri:value="https://e.com/i.png"/></ac:image>')
        assert doc.content[0].kind == "image"

        # table
        doc = self.parser.parse('<table><tbody><tr><td>a</td></tr></tbody></table>')
        assert doc.content[0].kind == "table"

        # code block
        doc = self.parser.parse('<ac:structured-macro ac:name="code" ac:macro-id="m"><ac:plain-text-body><![CDATA[x]]></ac:plain-text-body></ac:structured-macro>')
        assert doc.content[0].kind == "code_block"

        # panel
        doc = self.parser.parse('<ac:structured-macro ac:name="panel" ac:macro-id="p"/>')
        assert doc.content[0].kind == "macro:panel"

        # notification (info)
        doc = self.parser.parse('<ac:structured-macro ac:name="info" ac:macro-id="i"/>')
        assert doc.content[0].kind == "macro:notification"

        # jira
        doc = self.parser.parse('<ac:structured-macro ac:name="jira" ac:macro-id="j"/>')
        assert doc.content[0].kind == "macro:jira"

        # toc
        doc = self.parser.parse('<ac:structured-macro ac:name="toc" ac:macro-id="t"/>')
        assert doc.content[0].kind == "macro:toc"

        # expand
        doc = self.parser.parse('<ac:structured-macro ac:name="expand" ac:macro-id="e"/>')
        assert doc.content[0].kind == "macro:expand"

        # view-file
        doc = self.parser.parse('<ac:structured-macro ac:name="view-file" ac:macro-id="vf"/>')
        assert doc.content[0].kind == "macro:view_file"

        # gadget
        doc = self.parser.parse('<ac:structured-macro ac:name="gadget" ac:macro-id="g"/>')
        assert doc.content[0].kind == "macro:gadget"

        # anchor
        doc = self.parser.parse('<ac:structured-macro ac:name="anchor" ac:macro-id="a"/>')
        assert doc.content[0].kind == "macro:anchor"

        # excerpt
        doc = self.parser.parse('<ac:structured-macro ac:name="excerpt" ac:macro-id="ex"/>')
        assert doc.content[0].kind == "macro:excerpt"

        # excerpt-include
        doc = self.parser.parse('<ac:structured-macro ac:name="excerpt-include" ac:macro-id="exi"/>')
        assert doc.content[0].kind == "macro:excerpt_include"

        # page-properties
        doc = self.parser.parse('<ac:structured-macro ac:name="page-properties" ac:macro-id="pp"/>')
        assert doc.content[0].kind == "macro:page_properties"

        # page-properties-report
        doc = self.parser.parse('<ac:structured-macro ac:name="page-properties-report" ac:macro-id="ppr"/>')
        assert doc.content[0].kind == "macro:page_properties_report"

        # children-display
        doc = self.parser.parse('<ac:structured-macro ac:name="children-display" ac:macro-id="cd"/>')
        assert doc.content[0].kind == "macro:children_display"

        # attachments
        doc = self.parser.parse('<ac:structured-macro ac:name="attachments" ac:macro-id="att"/>')
        assert doc.content[0].kind == "macro:attachments"

        # adf_node
        doc = self.parser.parse('<ac:adf-node type="x"/>')
        assert doc.content[0].kind == "adf_node"

        # adf_fallback (via direct)
        doc = self.parser.parse('<ac:adf-fallback>f</ac:adf-fallback>')
        assert doc.content[0].kind == "adf_fallback"

        # adf_extension
        doc = self.parser.parse('<ac:adf-extension/>')
        assert doc.content[0].kind == "adf_extension"

        # decision_list, task, task_list, task_list_container
        doc = self.parser.parse('<ac:task ac:local-id="1" ac:task-id="1"/>')
        assert doc.content[0].kind == "task"
        doc = self.parser.parse('<ac:task-list/>')
        assert doc.content[0].kind == "task_list_container"
        doc = self.parser.parse('<ac:structured-macro ac:name="task-list" ac:macro-id="t1"><ac:task-item ac:local-id="i" ac:task-id="t"/></ac:structured-macro>')
        assert doc.content[0].kind in {"task_list","macro"}

        # emoticon
        doc = self.parser.parse('<ac:emoticon ac:name="blue-star"/>')
        assert doc.content[0].kind == "emoticon"

        # blockquote
        doc = self.parser.parse('<blockquote><p>x</p></blockquote>')
        assert doc.content[0].kind == "blockquote"

        # layout, layout_section, layout_cell kinds
        doc = self.parser.parse('<ac:layout><ac:layout-section ac:type="fixed-width"><ac:layout-cell><p>x</p></ac:layout-cell></ac:layout-section></ac:layout>')
        layout = doc.content[0]
        assert layout.kind == "layout"
        sec = layout.children[0]
        assert sec.kind == "layout_section"
        # standalone layout-cell to ensure element with type=layout_cell exists
        doc = self.parser.parse('<ac:layout-cell><p>x</p></ac:layout-cell>')
        assert doc.content[0].kind == "layout_cell"

        # placeholder
        doc = self.parser.parse('<ac:placeholder ac:type="mention">@u</ac:placeholder>')
        assert doc.content[0].kind == "placeholder"

        # inline_comment
        doc = self.parser.parse('<ac:inline-comment-marker ac:ref="r">t</ac:inline-comment-marker>')
        assert doc.content[0].kind == "inline_comment"

        # status
        doc = self.parser.parse('<ac:structured-macro ac:name="status" ac:macro-id="s"/>')
        assert doc.content[0].kind == "status"

        # date
        doc = self.parser.parse('<time datetime="2024-01-01"/>')
        assert doc.content[0].kind == "date"

