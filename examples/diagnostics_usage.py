#!/usr/bin/env python3
"""
Diagnostics usage example for Confluence Content Parser.

This example demonstrates:
- How to handle parsing errors and diagnostics
- Unknown elements and macros
- Unicode and encoding issues
- Best practices for robust parsing
- Troubleshooting common issues
"""

from confluence_content_parser import ConfluenceParser


def main():
    problematic_content = """
    <h1>Diagnostics Example</h1>

    <p>This content contains various elements that will generate diagnostics:</p>

    <!-- Unknown macro that doesn't exist -->
    <ac:structured-macro ac:name="unknown-macro" ac:schema-version="1">
        <ac:parameter ac:name="param1">value1</ac:parameter>
        <ac:rich-text-body>
            <p>This macro is not implemented</p>
        </ac:rich-text-body>
    </ac:structured-macro>

    <!-- Known elements -->
    <ac:structured-macro ac:name="details" ac:schema-version="1">
        <ac:rich-text-body>
            <table>
                <tr><th>Field</th><th>Value</th></tr>
                <tr><td>Status</td><td><ac:structured-macro ac:name="status">
                    <ac:parameter ac:name="title">Active</ac:parameter>
                    <ac:parameter ac:name="colour">Green</ac:parameter>
                </ac:structured-macro></td></tr>
            </table>
        </ac:rich-text-body>
    </ac:structured-macro>

    <!-- Links to various resources -->
    <h2>Links Example</h2>
    <ul>
        <li>External URL: <ac:link><ri:url ri:value="https://example.com"/></ac:link></li>
        <li>Page link: <ac:link><ri:page ri:space-key="DOC" ri:content-title="User Guide"/></ac:link></li>
        <li>User mention: <ac:link><ri:user ri:account-id="user123"/></ac:link></li>
        <li>Attachment: <ac:link><ri:attachment ri:filename="document.pdf"/></ac:link></li>
    </ul>

    <!-- Task list -->
    <h2>Tasks</h2>
    <ac:task-list>
        <ac:task>
            <ac:task-id>task1</ac:task-id>
            <ac:task-status>complete</ac:task-status>
            <ac:task-body>Review documentation</ac:task-body>
        </ac:task>
        <ac:task>
            <ac:task-id>task2</ac:task-id>
            <ac:task-status>incomplete</ac:task-status>
            <ac:task-body><ac:placeholder>Add task description here</ac:placeholder></ac:task-body>
        </ac:task>
    </ac:task-list>

    <!-- Unknown elements (these will be skipped) -->
    <unknown-element>This should be skipped</unknown-element>

    <!-- Inline comment marker (should be skipped) -->
    <p>Some text with <ac:inline-comment-marker ac:ref="comment-123">inline comment</ac:inline-comment-marker></p>

    <!-- Panel with content -->
    <ac:structured-macro ac:name="panel" ac:schema-version="1">
        <ac:parameter ac:name="title">Important Note</ac:parameter>
        <ac:parameter ac:name="bgColor">#FFF2CC</ac:parameter>
        <ac:rich-text-body>
            <p>This is a panel with <strong>formatted content</strong> and placeholders:</p>
            <p><ac:placeholder>Add important information here</ac:placeholder></p>
        </ac:rich-text-body>
    </ac:structured-macro>
    """

    print("=== DIAGNOSTICS EXAMPLE ===\n")

    # Parse with diagnostics enabled (default)
    print("1. PARSING WITH DIAGNOSTICS:")
    parser = ConfluenceParser(raise_on_finish=False)  # Don't raise errors, collect diagnostics
    doc = parser.parse(problematic_content)

    print(f"   Document parsed successfully: {doc.root is not None}")
    print(f"   Total elements found: {len(doc.walk())}")
    print()

    # Check diagnostics
    print("2. PARSING DIAGNOSTICS:")
    diagnostics = doc.metadata.get("diagnostics", [])
    if diagnostics:
        print(f"   Found {len(diagnostics)} diagnostic messages:")
        for i, diag in enumerate(diagnostics, 1):
            print(f"     {i}. {diag}")
    else:
        print("   No diagnostic messages (all elements parsed successfully)")
    print()

    # Analyze what was successfully parsed
    print("3. SUCCESSFULLY PARSED ELEMENTS:")

    # Count different types of elements
    from confluence_content_parser import (
        DetailsMacro,
        HeadingElement,
        LinkElement,
        ListElement,
        PanelMacro,
        PlaceholderElement,
        StatusMacro,
        Table,
    )

    element_counts = {
        "Headings": len(doc.find_all(HeadingElement)),
        "Status macros": len(doc.find_all(StatusMacro)),
        "Details macros": len(doc.find_all(DetailsMacro)),
        "Placeholders": len(doc.find_all(PlaceholderElement)),
        "Links": len(doc.find_all(LinkElement)),
        "Task lists": len(
            [
                list_element
                for list_element in doc.find_all(ListElement)
                if hasattr(list_element.type, "value") and list_element.type.value == "task-list"
            ]
        ),
        "Panels": len(doc.find_all(PanelMacro)),
        "Tables": len(doc.find_all(Table)),
    }

    for element_type, count in element_counts.items():
        print(f"   {element_type}: {count}")
    print()

    # Link analysis with type breakdown
    print("4. LINK ANALYSIS:")
    links = doc.find_all(LinkElement)
    if links:
        link_types = {}
        for link in links:
            link_type = link.type.value if hasattr(link.type, "value") else str(link.type)
            link_types[link_type] = link_types.get(link_type, 0) + 1

        for link_type, count in link_types.items():
            print(f"   {link_type} links: {count}")

        print("\n   Link details:")
        for i, link in enumerate(links, 1):
            link_text = link.to_text().strip()
            link_type = link.type.value if hasattr(link.type, "value") else str(link.type)
            print(f"     {i}. {link_type}: {link_text}")
    else:
        print("   No links found")
    print()

    # Placeholder analysis
    print("5. PLACEHOLDER ANALYSIS:")
    placeholders = doc.find_all(PlaceholderElement)
    if placeholders:
        print(f"   Found {len(placeholders)} placeholders:")
        for i, placeholder in enumerate(placeholders, 1):
            print(f"     {i}. {placeholder.to_text()}")
    else:
        print("   No placeholders found")
    print()

    # Document text extraction
    print("6. CLEAN TEXT OUTPUT:")
    print("   " + "=" * 47)
    clean_text = doc.text
    # Show first few lines of clean text
    text_lines = clean_text.split("\n")[:10]
    for line in text_lines:
        if line.strip():
            print(f"   {line.strip()}")
    if len(clean_text.split("\n")) > 10:
        print("   ... (truncated)")
    print("   " + "=" * 47)
    print()

    # Error handling example
    print("7. ERROR HANDLING EXAMPLE:")
    try:
        # Try parsing with raise_on_finish=True
        strict_parser = ConfluenceParser(raise_on_finish=True)
        strict_parser.parse(problematic_content)
        print("   Strict parsing succeeded (no unknown elements)")
    except Exception as e:
        print(f"   Strict parsing failed as expected: {type(e).__name__}")
        print(f"   Error details: {str(e)}")
    print()

    # Best practices
    print("8. PARSING STATISTICS:")
    total_elements = len(doc.walk())
    successful_elements = total_elements
    failed_elements = len(diagnostics)

    if total_elements > 0:
        success_rate = ((successful_elements) / (successful_elements + failed_elements)) * 100
        print(f"   Total parsed elements: {successful_elements}")
        print(f"   Failed/unknown elements: {failed_elements}")
        print(f"   Success rate: {success_rate:.1f}%")

    print(f"   Document length: {len(clean_text)} characters")
    print(f"   Non-empty lines: {len([line for line in clean_text.split('\\n') if line.strip()])}")


if __name__ == "__main__":
    main()
