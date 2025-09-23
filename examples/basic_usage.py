#!/usr/bin/env python3
"""
Basic usage example for Confluence Content Parser.

This example demonstrates core parsing capabilities including:
- Text formatting (bold, italic, code)
- Links and references
- Status macros
- Tables
- Lists and task lists
- Details macros with placeholders
"""

from confluence_content_parser import ConfluenceParser


def main():
    confluence_content = """
    <h1>Project Documentation</h1>

    <p>This document demonstrates <strong>basic parsing</strong> of Confluence content with <em>formatting</em> and <code>inline code</code>.</p>

    <h2>Project Status</h2>
    <p>Current status: <ac:structured-macro ac:name="status">
        <ac:parameter ac:name="title">In Progress</ac:parameter>
        <ac:parameter ac:name="colour">Yellow</ac:parameter>
    </ac:structured-macro></p>

    <h2>Team Information</h2>
    <ac:structured-macro ac:name="details">
        <ac:rich-text-body>
            <table>
                <tr><th>Role</th><th>Assignee</th></tr>
                <tr><td>Project Lead</td><td><ac:placeholder>@ mention lead</ac:placeholder></td></tr>
                <tr><td>Developer</td><td><ac:placeholder>@ mention developer</ac:placeholder></td></tr>
                <tr><td>QA Engineer</td><td><ac:placeholder>@ mention qa</ac:placeholder></td></tr>
            </table>
        </ac:rich-text-body>
    </ac:structured-macro>

    <h2>Tasks</h2>
    <ac:task-list>
        <ac:task>
            <ac:task-id>1</ac:task-id>
            <ac:task-status>complete</ac:task-status>
            <ac:task-body>Set up project repository</ac:task-body>
        </ac:task>
        <ac:task>
            <ac:task-id>2</ac:task-id>
            <ac:task-status>incomplete</ac:task-status>
            <ac:task-body>Implement core features</ac:task-body>
        </ac:task>
    </ac:task-list>

    <h2>External Resources</h2>
    <ul>
        <li>Documentation: <ac:link><ri:url ri:value="https://docs.example.com"/></ac:link></li>
        <li>Repository: <ac:link><ri:url ri:value="https://github.com/example/project"/></ac:link></li>
    </ul>
    """

    # Parse the content
    parser = ConfluenceParser()
    document = parser.parse(confluence_content)

    print("=== BASIC CONFLUENCE PARSING EXAMPLE ===\n")

    # Get clean text output
    print("1. DOCUMENT TEXT:")
    print(document.text)
    print("\n" + "=" * 50 + "\n")

    # Extract specific elements using find_all
    print("2. HEADINGS:")
    from confluence_content_parser import HeadingElement

    headings = document.find_all(HeadingElement)
    for heading in headings:
        print(f"  H{heading.type.value[-1]}: {heading.to_text()}")
    print()

    print("3. STATUS ELEMENTS:")
    from confluence_content_parser import StatusMacro

    status_elements = document.find_all(StatusMacro)
    for status in status_elements:
        print(f"  {status.to_text()}")
    print()

    print("4. TABLES:")
    from confluence_content_parser import Table

    tables = document.find_all(Table)
    for i, table in enumerate(tables, 1):
        print(f"  Table {i}: {len(table.children)} rows")
        print(f"    Content: {table.to_text()}")
    print()

    print("5. LINKS:")
    from confluence_content_parser import LinkElement

    links = document.find_all(LinkElement)
    for link in links:
        print(f"  {link.to_text()}")
    print()

    print("6. TASK LISTS:")
    from confluence_content_parser import ListElement, ListType

    lists = document.find_all(ListElement)
    task_lists = [list_element for list_element in lists if list_element.type == ListType.TASK]
    for task_list in task_lists:
        print(f"  Tasks: {task_list.to_text()}")
    print()

    print("7. PLACEHOLDER ELEMENTS:")
    from confluence_content_parser import PlaceholderElement

    placeholders = document.find_all(PlaceholderElement)
    for placeholder in placeholders:
        print(f"  {placeholder.to_text()}")
    print()

    print("8. DETAILS MACROS:")
    from confluence_content_parser import DetailsMacro

    details = document.find_all(DetailsMacro)
    for detail in details:
        print(f"  {detail.to_text()}")
    print()

    print("9. MULTIPLE TYPE SEARCH:")
    # Find multiple element types at once
    headings_multi, status_multi, placeholders_multi = document.find_all(
        HeadingElement, StatusMacro, PlaceholderElement
    )
    print(f"  Found in one search: {len(headings_multi)} headings, {len(status_multi)} status elements, {len(placeholders_multi)} placeholders")

    # Compare with individual searches (should match)
    assert len(headings_multi) == len(headings)
    assert len(status_multi) == len(status_elements)
    assert len(placeholders_multi) == len(placeholders)
    print("  ✓ Results match individual searches")
    print()

    # Document statistics
    all_nodes = document.walk()
    print("10. DOCUMENT STATISTICS:")
    print(f"  Total nodes: {len(all_nodes)}")
    print(f"  Headings: {len(headings)}")
    print(f"  Tables: {len(tables)}")
    print(f"  Links: {len(links)}")
    print(f"  Status elements: {len(status_elements)}")
    print(f"  Placeholders: {len(placeholders)}")
    print(f"  Details macros: {len(details)}")

    # Check for any parsing issues
    diagnostics = document.metadata.get("diagnostics", [])
    if diagnostics:
        print(f"\n11. PARSING DIAGNOSTICS: {diagnostics}")
    else:
        print("\n11. PARSING: No issues detected ✓")


if __name__ == "__main__":
    main()
