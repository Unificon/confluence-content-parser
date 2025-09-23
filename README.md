# Confluence Content Parser

> Important: This is an early-stage release. The API may change and using it in production carries risk. Pin versions and evaluate carefully before deployment.

[![PyPI version](https://img.shields.io/pypi/v/confluence-content-parser)](https://pypi.org/project/confluence-content-parser/)
[![Python versions](https://img.shields.io/pypi/pyversions/confluence-content-parser)](https://pypi.org/project/confluence-content-parser/)
[![CI](https://github.com/Unificon/confluence-content-parser/actions/workflows/ci.yml/badge.svg)](https://github.com/Unificon/confluence-content-parser/actions/workflows/ci.yml)
[![Coverage](https://codecov.io/github/Unificon/confluence-content-parser/graph/badge.svg?token=NRLLDJUCWG)](https://codecov.io/github/Unificon/confluence-content-parser)
[![License](https://img.shields.io/github/license/Unificon/confluence-content-parser)](LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A powerful and comprehensive Python library for parsing Confluence Storage Format content into structured data models using Pydantic.

## Features

✨ **Comprehensive Coverage**: Supports 40+ Confluence Storage Format elements and macros  
🚀 **High Performance**: Built with lxml for fast XML parsing  
🏗️ **Structured Data**: Uses Pydantic models for type-safe, validated data structures  
📝 **Modern Python**: Built for Python 3.12+ with full type hints  
🔧 **Extensible**: Clean architecture makes it easy to add new element types

## Installation

```bash
# Using uv (recommended)
uv add confluence-content-parser

# Using pip
pip install confluence-content-parser
```

## Quick Start

```python
from confluence_content_parser import ConfluenceParser

# Initialize the parser
parser = ConfluenceParser()

# Parse Confluence Storage Format content
content = """
<ac:layout>
    <ac:layout-section ac:type="fixed-width">
        <ac:layout-cell>
            <h2>My Document</h2>
            <p>This is a <strong>bold</strong> paragraph.</p>
            <ac:structured-macro ac:name="info">
                <ac:rich-text-body>
                    <p>This is an info panel.</p>
                </ac:rich-text-body>
            </ac:structured-macro>
        </ac:layout-cell>
    </ac:layout-section>
</ac:layout>
"""

# Parse the content
document = parser.parse(content)

# Access the structured data
print(f"Document text: {document.text}")

# Find all nodes of specific types
from confluence_content_parser import HeadingElement, PanelMacro

headings = document.find_all(HeadingElement)
panels = document.find_all(PanelMacro)

# Or find multiple types at once
headings, panels = document.find_all(HeadingElement, PanelMacro)

print(f"Found {len(headings)} headings and {len(panels)} panels")

# Navigate the structure
for node in document.walk():
    print(f"Node type: {type(node).__name__}")
```

## Examples

- `examples/basic_usage.py`: Basic parsing, text extraction, and element traversal
- `examples/advanced_usage.py`: Complex layouts, macros, nested content analysis  
- `examples/diagnostics_usage.py`: Error handling, unknown elements, and parsing diagnostics

## Supported Elements & Macros

### Text Elements
| Element | Node Class | Description |
|---------|------------|-------------|
| `<p>` | `TextBreakElement` | Paragraph with text and formatting |
| `<h1>`-`<h6>` | `HeadingElement` | Heading levels 1-6 |
| `<strong>`, `<em>`, `<u>` | `TextEffectElement` | Bold, italic, underline |
| `<sub>`, `<sup>`, `<del>` | `TextEffectElement` | Subscript, superscript, strikethrough |
| `<blockquote>` | `TextEffectElement` | Block quotations |
| `<span>` | `TextEffectElement` | Inline text with styling |
| `<code>` | `TextEffectElement` | Inline code formatting |
| Text content | `Text` | Plain text nodes |

### Lists & Structure
| Element | Node Class | Description |
|---------|------------|-------------|
| `<ul>`, `<ol>` | `ListElement` | Unordered and ordered lists |
| `<li>` | `ListItem` | List items (regular and tasks) |
| `<ac:task-list>` | `ListElement` | Task lists |
| `<ac:task>` | `ListItem` | Individual task items |
| `<table>` | `Table` | Tables with headers and data |
| `<tr>` | `TableRow` | Table rows |
| `<td>`, `<th>` | `TableCell` | Table cells |
| `<hr>` | `TextBreakElement` | Horizontal dividers |
| `<br>` | `TextBreakElement` | Line breaks |

### Layout Elements
| Element | Node Class | Description |
|---------|------------|-------------|
| `<ac:layout>` | `LayoutElement` | Page layout container |
| `<ac:layout-section>` | `LayoutSection` | Layout section with columns |
| `<ac:layout-cell>` | `LayoutCell` | Individual layout cell |

### Media Elements
| Element | Node Class | Description |
|---------|------------|-------------|
| `<ac:image>` | `Image` | Images with attachments or URLs |

### Interactive Elements
| Element | Node Class | Description |
|---------|------------|-------------|
| `<ac:link>` | `LinkElement` | Links to pages, users, attachments |
| `<a>` | `LinkElement` | External links and mailto |
| `<ac:emoticon>` | `Emoticon` | Confluence emoticons and emojis |
| `<ac:placeholder>` | `PlaceholderElement` | Dynamic content placeholders |
| `<time>` | `Time` | Date and time elements |
| `<ri:*>` | `ResourceIdentifier` | Resource identifiers (pages, attachments, etc.) |

### Macros
| Macro | Node Class | Description |
|-------|------------|-------------|
| `info`, `warning`, `note`, `tip` | `PanelMacro` | Notification panels |
| `panel` | `PanelMacro` | Custom styled panels |
| `code` | `CodeMacro` | Syntax-highlighted code blocks |
| `status` | `StatusMacro` | Status indicators |
| `jira` | `JiraMacro` | JIRA issue integration |
| `expand` | `ExpandMacro` | Expandable content sections |
| `details` | `DetailsMacro` | Collapsible content sections |
| `toc` | `TocMacro` | Auto-generated table of contents |
| `view-file` | `ViewFileMacro` | File preview macro |
| `viewpdf` | `ViewPdfMacro` | PDF viewer macro |
| `excerpt` | `ExcerptMacro` | Content excerpts |
| `excerpt-include` | `ExcerptIncludeMacro` | Include content excerpts |
| `include` | `IncludeMacro` | Include other pages |
| `attachments` | `AttachmentsMacro` | List page attachments |
| `profile` | `ProfileMacro` | User profile display |
| `anchor` | `AnchorMacro` | Page anchors |
| `tasks-report-macro` | `TasksReportMacro` | Task reports |

### Advanced Elements
| Element | Node Class | Description |
|---------|------------|-------------|
| `<ac:adf-extension>` | `PanelMacro`, `DecisionList` | ADF panel and decision list extensions |
| Decision lists | `DecisionList` | Decision tracking lists |
| Decision items | `DecisionListItem` | Individual decision items |
| Fragment | `Fragment` | Container for multiple top-level nodes |

## Advanced Usage

### Working with Structured Data

```python
from confluence_content_parser import ConfluenceParser, Image, ListElement, ListType

parser = ConfluenceParser()
document = parser.parse(confluence_content)

# Find all images in the document
images = document.find_all(Image)
for image in images:
    print(f"Image: {image.alt or 'No alt text'} ({image.width}x{image.height})")

# Find all task lists
all_lists = document.find_all(ListElement)
task_lists = [lst for lst in all_lists if lst.type == ListType.TASK]
for task_list in task_lists:
    print(f"Task list with {len(task_list.children)} tasks")

# Analyze content structure efficiently
images, tables, links = document.find_all(Image, Table, LinkElement)
print(f"Document contains: {len(images)} images, {len(tables)} tables, {len(links)} links")

# Walk through all nodes in the document
for node in document.walk():
    if hasattr(node, 'text') and node.text:
        print(f"Text node: {node.text[:50]}...")
```

### Custom Processing

```python
from confluence_content_parser import ConfluenceParser, Text

parser = ConfluenceParser()
document = parser.parse(content)

# Extract all text content (built-in method)
full_text = document.text
print(f"Document text: {full_text}")

# Or manually collect text nodes
text_nodes = document.find_all(Text)
all_text = " ".join(node.text for node in text_nodes)
print(f"All text: {all_text}")

# Custom traversal
def find_nodes_with_condition(document, condition_func):
    """Find all nodes matching a custom condition."""
    matching_nodes = []
    for node in document.walk():
        if condition_func(node):
            matching_nodes.append(node)
    return matching_nodes

# Example: Find all nodes that contain specific text
nodes_with_api = find_nodes_with_condition(
    document, 
    lambda node: hasattr(node, 'text') and 'API' in getattr(node, 'text', '')
)
```

### Error Handling

```python
from confluence_content_parser import ConfluenceParser, ParsingError
import xml.etree.ElementTree as ET

# Default behavior: collect diagnostics without raising errors
parser = ConfluenceParser(raise_on_finish=False)

try:
    document = parser.parse(malformed_content)
    # Check diagnostics for any issues
    diagnostics = document.metadata.get("diagnostics", [])
    if diagnostics:
        print(f"Parsing issues found: {diagnostics}")
except ET.ParseError as e:
    print(f"XML parsing error: {e}")

# Strict parsing: raise errors for unknown elements
strict_parser = ConfluenceParser(raise_on_finish=True)
try:
    document = strict_parser.parse(content_with_unknown_elements)
except ParsingError as e:
    print(f"Parsing failed with diagnostics: {e.diagnostics}")
```

### Diagnostics

The parser collects non-fatal parsing notes (e.g., unknown macros) in `document.metadata["diagnostics"]`.

```python
from confluence_content_parser import ConfluenceParser

parser = ConfluenceParser(raise_on_finish=False)
doc = parser.parse('<ac:structured-macro ac:name="unknown-macro"/>')
diagnostics = doc.metadata.get("diagnostics", [])
for diagnostic in diagnostics:
    print(diagnostic)  # Outputs: unknown_macro:unknown-macro
# See examples/diagnostics_usage.py for a complete example
```

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/Unificon/confluence-content-parser.git
cd confluence-content-parser

# Install dependencies with uv
uv sync --dev

# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=confluence_content_parser --cov-report=html
```

### Project Structure

```
src/confluence_content_parser/
├── __init__.py           # Main exports
├── parser.py            # Core parser implementation
├── document.py          # ConfluenceDocument model
└── nodes.py             # All node types and models
```

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage report
uv run pytest --cov=confluence_content_parser --cov-report=term-missing

# Run specific test file
uv run pytest tests/test_parser.py

# Run with verbose output
uv run pytest -v
```

### Code Quality

```bash
# Format code
uv run black src/ tests/

# Lint code  
uv run ruff check src/ tests/

# Type checking
uv run mypy src/
```

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Workflow

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes with tests
4. Ensure all tests pass: `uv run pytest`
5. Submit a pull request

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [lxml](https://lxml.de/) for robust XML parsing
- Uses [Pydantic](https://pydantic.dev/) for data validation and serialization
- Uses [types-lxml](https://github.com/abelcheung/types-lxml) for `lxml` type annotations
- Inspired by the Confluence Storage Format specification