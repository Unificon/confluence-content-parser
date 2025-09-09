#!/usr/bin/env python3
"""Basic usage example for confluence-content-parser."""

from confluence_content_parser import ConfluenceParser


def main():
    """Demonstrate basic usage of the parser."""
    # Sample Confluence Storage Format content
    confluence_content = '''
    <ac:layout>
        <ac:layout-section ac:type="fixed-width" ac:breakout-mode="default">
            <ac:layout-cell>
                <p>This is a sample paragraph with <strong>bold text</strong> and <em>italic text</em>.</p>
                <p>Here's a link to a user: <ac:link><ri:user ri:account-id="123456" ri:local-id="user-id"/></ac:link></p>
                <ac:structured-macro ac:name="status" ac:macro-id="status-1">
                    <ac:parameter ac:name="title">In Progress</ac:parameter>
                    <ac:parameter ac:name="colour">Blue</ac:parameter>
                </ac:structured-macro>
                <table data-table-width="500">
                    <tbody>
                        <tr>
                            <th><p>Name</p></th>
                            <th><p>Value</p></th>
                        </tr>
                        <tr>
                            <td><p>Item 1</p></td>
                            <td><p>Value 1</p></td>
                        </tr>
                        <tr>
                            <td><p>Item 2</p></td>
                            <td><p>Value 2</p></td>
                        </tr>
                    </tbody>
                </table>
            </ac:layout-cell>
        </ac:layout-section>
    </ac:layout>
    '''

    # Create parser instance
    parser = ConfluenceParser()

    # Parse the content
    document = parser.parse(confluence_content)

    # Display parsed structure
    print("Parsed Confluence Document:")
    print(f"Number of top-level elements: {len(document.content)}")
    print()

    # Recursively print the structure
    def print_element(element, indent=0):
        """Print element structure recursively."""
        prefix = "  " * indent
        print(f"{prefix}- Type: {element.type}")

        if element.text:
            print(f"{prefix}  Text: {element.text}")

        if element.link:
            print(f"{prefix}  Link URL: {element.link.url}")
            print(f"{prefix}  Link Text: {element.link.text}")
            if element.link.user_reference:
                print(f"{prefix}  User Account ID: {element.link.user_reference.account_id}")

        if element.status:
            print(f"{prefix}  Status Title: {element.status.title}")
            print(f"{prefix}  Status Color: {element.status.colour}")

        if element.table:
            cells = element.table.cells
            if cells:
                headers = [" ".join((c.text or c.text_normalized()) for c in cell).strip() for cell in cells[0]]
                print(f"{prefix}  Table Headers: {headers}")
                for r_idx, row in enumerate(cells[1:], start=1):
                    row_texts = [" ".join((c.text or c.text_normalized()) for c in cell).strip() for cell in row]
                    print(f"{prefix}  Row {r_idx}: {row_texts}")

        if element.layout_section:
            print(f"{prefix}  Layout Type: {element.layout_section.type}")
            print(f"{prefix}  Layout Cells: {len(element.layout_section.cells)}")

        if element.macro:
            print(f"{prefix}  Macro Name: {element.macro.name}")
            print(f"{prefix}  Macro Parameters: {element.macro.parameters}")

        # Print children
        for child in element.children:
            print_element(child, indent + 1)

        # Print layout cell content
        if element.layout_section:
            for i, cell in enumerate(element.layout_section.cells):
                print(f"{prefix}  Cell {i+1}:")
                for cell_element in cell.content:
                    print_element(cell_element, indent + 2)

    for element in document.content:
        print_element(element)

    print("\nJSON representation:")
    print(document.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
