#!/usr/bin/env python3
"""
Advanced usage example for Confluence Content Parser.

This example demonstrates more complex parsing scenarios including:
- Nested macros and layouts
- Panel and expand macros
- Code blocks and attachments
- Complex table structures
- Media elements and emoticons
- Document traversal and filtering
"""

from confluence_content_parser import ConfluenceParser


def main():
    content = """
    <ac:layout>
      <ac:layout-section ac:type="two_equal">
        <ac:layout-cell>
          <h1><ac:emoticon ac:name="blue-star" ac:emoji-shortname=":star:" ac:emoji-id="2b50" ac:emoji-fallback="⭐" />&nbsp;API Documentation</h1>

          <ac:structured-macro ac:name="panel" ac:schema-version="1">
            <ac:parameter ac:name="bgColor">#E3FCEF</ac:parameter>
            <ac:parameter ac:name="title">Quick Start Guide</ac:parameter>
            <ac:rich-text-body>
              <p>Follow these steps to get started with our API:</p>
              <ol>
                <li>Get your API key from the <ac:link><ri:url ri:value="https://api.example.com/keys"/></ac:link></li>
                <li>Review the authentication guide</li>
                <li>Try the sample requests below</li>
              </ol>
            </ac:rich-text-body>
          </ac:structured-macro>

          <h2>Authentication</h2>
          <ac:structured-macro ac:name="code" ac:schema-version="1">
            <ac:parameter ac:name="language">bash</ac:parameter>
            <ac:plain-text-body><![CDATA[curl -H "Authorization: Bearer YOUR_API_KEY" \
  https://api.example.com/v1/users]]></ac:plain-text-body>
          </ac:structured-macro>

          <h2>Status Indicators</h2>
          <table>
            <tr>
              <th>Endpoint</th>
              <th>Status</th>
              <th>Last Updated</th>
            </tr>
            <tr>
              <td>/users</td>
              <td><ac:structured-macro ac:name="status">
                <ac:parameter ac:name="title">Stable</ac:parameter>
                <ac:parameter ac:name="colour">Green</ac:parameter>
              </ac:structured-macro></td>
              <td><ac:time ac:datetime="2024-01-15T10:30:00Z" /></td>
            </tr>
            <tr>
              <td>/orders</td>
              <td><ac:structured-macro ac:name="status">
                <ac:parameter ac:name="title">Beta</ac:parameter>
                <ac:parameter ac:name="colour">Yellow</ac:parameter>
              </ac:structured-macro></td>
              <td><ac:time ac:datetime="2024-01-10T14:15:00Z" /></td>
            </tr>
          </table>
        </ac:layout-cell>

        <ac:layout-cell>
          <h2>Response Examples</h2>

          <ac:structured-macro ac:name="expand" ac:schema-version="1">
            <ac:parameter ac:name="title">GET /users Response</ac:parameter>
            <ac:rich-text-body>
              <ac:structured-macro ac:name="code" ac:schema-version="1">
                <ac:parameter ac:name="language">json</ac:parameter>
                <ac:plain-text-body><![CDATA[{
  "users": [
    {
      "id": 123,
      "name": "John Doe",
      "email": "john@example.com",
      "status": "active"
    }
  ],
  "pagination": {
    "page": 1,
    "total": 50
  }
}]]></ac:plain-text-body>
              </ac:structured-macro>
            </ac:rich-text-body>
          </ac:structured-macro>

          <h3>Error Handling</h3>
          <ac:structured-macro ac:name="info" ac:schema-version="1">
            <ac:rich-text-body>
              <p>All API errors return standard HTTP status codes with JSON error details.</p>
              <p>See our <ac:link><ri:page ri:space-key="DEV" ri:content-title="Error Codes"/></ac:link> page for details.</p>
            </ac:rich-text-body>
          </ac:structured-macro>

          <h3>Attachments</h3>
          <p>Example image: <ac:image ac:width="150"><ri:attachment ri:filename="api-flow.png"/></ac:image></p>

          <ac:structured-macro ac:name="attachments" ac:schema-version="1"/>
        </ac:layout-cell>
      </ac:layout-section>
    </ac:layout>
    """

    # Parse with diagnostics enabled
    parser = ConfluenceParser(raise_on_finish=False)
    doc = parser.parse(content)

    print("=== ADVANCED CONFLUENCE PARSING EXAMPLE ===\n")

    # 1. Document overview
    print("1. DOCUMENT OVERVIEW:")
    print(f"   Root type: {type(doc.root).__name__}")
    print(f"   Total elements: {len(doc.walk())}")
    print()

    # 2. Layout analysis
    print("2. LAYOUT STRUCTURE:")
    from confluence_content_parser import LayoutCell, LayoutElement, LayoutSection

    layouts = doc.find_all(LayoutElement)
    for i, layout in enumerate(layouts, 1):
        sections = [child for child in layout.children if isinstance(child, LayoutSection)]
        print(f"   Layout {i}: {len(sections)} sections")
        for j, section in enumerate(sections, 1):
            cells = [child for child in section.children if isinstance(child, LayoutCell)]
            print(f"     Section {j} ({section.section_type.value}): {len(cells)} cells")
    print()

    # 3. Macro analysis
    print("3. MACRO ANALYSIS:")
    from confluence_content_parser import AttachmentsMacro, CodeMacro, ExpandMacro, PanelMacro, StatusMacro

    macro_types = [
        (PanelMacro, "Panel"),
        (CodeMacro, "Code"),
        (ExpandMacro, "Expand"),
        (StatusMacro, "Status"),
        (AttachmentsMacro, "Attachments"),
    ]

    for macro_class, name in macro_types:
        macros = doc.find_all(macro_class)
        print(f"   {name} macros: {len(macros)}")
        for macro in macros:
            if hasattr(macro, "title") and macro.title:
                print(f"     - Title: {macro.title}")
            elif hasattr(macro, "language") and macro.language:
                print(f"     - Language: {macro.language}")
            elif hasattr(macro, "type"):
                print(f"     - Type: {macro.type.value}")
    print()

    # 4. Content extraction
    print("4. CONTENT EXTRACTION:")

    # Code blocks
    code_blocks = doc.find_all(CodeMacro)
    print(f"   Code blocks: {len(code_blocks)}")
    for i, code in enumerate(code_blocks, 1):
        lang = code.language or "text"
        lines = len(code.code.split("\n")) if code.code else 0
        print(f"     Block {i}: {lang} ({lines} lines)")

    # Tables
    from confluence_content_parser import Table, TableRow

    tables = doc.find_all(Table)
    print(f"   Tables: {len(tables)}")
    for i, table in enumerate(tables, 1):
        rows = [child for child in table.children if isinstance(child, TableRow)]
        print(f"     Table {i}: {len(rows)} rows")

    # Links
    from confluence_content_parser import LinkElement

    links = doc.find_all(LinkElement)
    print(f"   Links: {len(links)}")
    for link in links:
        print(f"     - {link.type.value}: {link.to_text()}")
    print()

    # 5. Media elements
    print("5. MEDIA ELEMENTS:")
    from confluence_content_parser import Emoticon, Image, Time

    images = doc.find_all(Image)
    print(f"   Images: {len(images)}")
    for img in images:
        if img.filename:
            print(f"     - {img.filename}")

    emoticons = doc.find_all(Emoticon)
    print(f"   Emoticons: {len(emoticons)}")
    for emoticon in emoticons:
        print(f"     - {emoticon.name or emoticon.emoji_shortname}")

    times = doc.find_all(Time)
    print(f"   Time elements: {len(times)}")
    for time_elem in times:
        print(f"     - {time_elem.datetime}")
    print()

    # 6. Text analysis
    print("6. TEXT ANALYSIS:")
    full_text = doc.text
    print(f"   Total characters: {len(full_text)}")
    print(f"   Lines: {len(full_text.split('\\n'))}")
    print(f"   Words (approx): {len(full_text.split())}")
    print()

    # 7. Nested content search
    print("7. NESTED CONTENT SEARCH:")
    panels = doc.find_all(PanelMacro)
    for i, panel in enumerate(panels, 1):
        nested_links = panel.find_all(LinkElement)
        nested_lists = panel.find_all()  # All nested elements
        print(f"   Panel {i}: {len(nested_links)} links, {len(nested_lists)} total nested elements")
    print()

    # 8. Document diagnostics
    print("8. PARSING DIAGNOSTICS:")
    diagnostics = doc.metadata.get("diagnostics", [])
    if diagnostics:
        for diag in diagnostics:
            print(f"   - {diag}")
    else:
        print("   No issues detected ✓")
    print()

    # 9. Export clean text
    print("9. CLEAN TEXT OUTPUT:")
    print("=" * 50)
    print(doc.text)
    print("=" * 50)


if __name__ == "__main__":
    main()
