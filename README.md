# Confluence Content Parser

[![Python Version](https://img.shields.io/badge/python-3.12+-blue.svg)](https://python.org)
[![Tests](https://img.shields.io/badge/tests-**passed-green.svg)](https://github.com/your-repo/confluence-content-parser)
[![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen.svg)](https://github.com/your-repo/confluence-content-parser)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-black-black.svg)](https://github.com/psf/black)

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
print(f"Document contains {len(document.content)} top-level elements")

# Navigate the structure
layout = document.content[0]
section = layout.children[0] 
cell_content = section.layout_section.cells[0].content

for element in cell_content:
    print(f"Element type: {element.type}")
```

## Examples

- `examples/basic_usage.py`: minimal parsing and traversal
- `examples/advanced_usage.py`: ids, paths, kinds, scopes, canonical URIs, table cells, helpers
- `examples/diagnostics_usage.py`: reading `document.metadata["diagnostics"]` and link normalization

## Supported Elements & Macros

### Text Elements
| Element | Type | Description |
|---------|------|-------------|
| `<p>` | paragraph | Paragraph with text and formatting |
| `<h1>`-`<h6>` | heading | Heading levels 1-6 |
| `<strong>`, `<em>`, `<u>` | text formatting | Bold, italic, underline |
| `<sub>`, `<sup>`, `<del>` | text formatting | Subscript, superscript, strikethrough |
| `<blockquote>` | quote | Block quotations |
| `<span>` | text span | Inline text with styling |

### Lists & Structure
| Element | Type | Description |
|---------|------|-------------|
| `<ul>`, `<ol>`, `<li>` | lists | Unordered and ordered lists |
| `<table>`, `<tr>`, `<td>`, `<th>` | table | Tables with headers and data |
| `<hr>` | horizontal rule | Horizontal dividers |
| `<br>` | line break | Line breaks |

### Layout Elements
| Element | Type | Description |
|---------|------|-------------|
| `<ac:layout>` | layout | Page layout container |
| `<ac:layout-section>` | layout section | Layout section with columns |
| `<ac:layout-cell>` | layout cell | Individual layout cell |

### Media Elements
| Element | Type | Description |
|---------|------|-------------|
| `<ac:image>` | image | Images with attachments or URLs |

### Interactive Elements
| Element | Type | Description |
|---------|------|-------------|
| `<ac:link>` | link | Links to pages, users, attachments |
| `<ac:task>` | task | Individual task elements |
| `<ac:task-list>` | task list | Task list containers |
| `<ac:emoticon>` | emoticon | Confluence emoticons and emojis |
| `<ac:placeholder>` | placeholder | Dynamic content placeholders |
| `<ac:inline-comment-marker>` | comment | Inline comment markers |
| `<time>` | date | Date and time elements |

### Macros
| Macro | Type | Description |
|-------|------|-------------|
| `info`, `warning`, `note`, `tip` | notification | Notification panels |
| `panel` | panel | Custom styled panels |
| `code` | code block | Syntax-highlighted code blocks |
| `status` | status | Status indicators |
| `jira` | jira | JIRA issue integration |
| `expand` | expand | Expandable content sections |
| `toc` | table of contents | Auto-generated table of contents |
| `view-file` | file viewer | File preview macro |
| `page-properties`, `page-properties-report` | page properties | Metadata tables and reports |
| `excerpt`, `excerpt-include` | excerpt | Reusable content snippets |
| `children-display` | children | List child pages |
| `attachments` | attachments | List page attachments |
| `gadget` | gadget | JIRA gadgets and widgets |

### Advanced Elements
| Element | Type | Description |
|---------|------|-------------|
| `<ac:adf-extension>` | ADF extension | Atlassian Document Format extensions |
| `<ac:adf-node>` | ADF node | ADF node structures |
| `<at:i18n>` | internationalization | I18n elements |

## Advanced Usage

### Working with Structured Data

```python
from confluence_content_parser import ConfluenceParser
from confluence_content_parser.models import ContentElement

parser = ConfluenceParser()
document = parser.parse(confluence_content)

def find_elements_by_type(elements: list[ContentElement], element_type: str):
    """Recursively find all elements of a specific type."""
    found = []
    for element in elements:
        if element.type == element_type:
            found.append(element)
        if hasattr(element, 'children') and element.children:
            found.extend(find_elements_by_type(element.children, element_type))
    return found

# Find all images in the document
images = find_elements_by_type(document.content, "image")
for image in images:
    print(f"Image: {image.image.alt} ({image.image.width}x{image.image.height})")

# Find all task lists
task_lists = find_elements_by_type(document.content, "task_list_container")
for task_list in task_lists:
    print(f"Task list with {len(task_list.task_list_container.tasks)} tasks")
```

### Custom Processing

```python
from confluence_content_parser import ConfluenceParser

def extract_text_content(element):
    """Extract plain text from any element."""
    text_parts = []
    
    if element.text:
        text_parts.append(element.text)
    
    if hasattr(element, 'children') and element.children:
        for child in element.children:
            text_parts.append(extract_text_content(child))
    
    return ' '.join(filter(None, text_parts))

parser = ConfluenceParser()
document = parser.parse(content)

# Extract all text content
full_text = ' '.join(extract_text_content(elem) for elem in document.content)
print(f"Document text: {full_text}")
```

### Error Handling

```python
from confluence_content_parser import ConfluenceParser
from lxml.etree import XMLSyntaxError

parser = ConfluenceParser()

try:
    document = parser.parse(malformed_content)
except XMLSyntaxError as e:
    print(f"XML parsing error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Diagnostics

The parser collects non-fatal parsing notes (e.g., unknown macros) in `document.metadata["diagnostics"]`.

```python
from confluence_content_parser import ConfluenceParser

parser = ConfluenceParser()
doc = parser.parse('<ac:structured-macro ac:name="xyz"/>')
diagnostics = doc.metadata.get("diagnostics") or []
for d in diagnostics:
    print(d)
# See examples/diagnostics_usage.py for a complete example
```

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/your-repo/confluence-content-parser.git
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
└── models/              # Pydantic data models
    ├── __init__.py      # Model exports
    ├── base.py          # Core ContentElement model
    ├── extensions.py    # Extension models (Panel, Task, etc.)
    ├── layout.py        # Layout models
    ├── links.py         # Link models  
    ├── macros.py        # Macro models
    ├── media.py         # Media models (Image)
    ├── metadata.py      # Metadata models
    ├── misc.py          # Miscellaneous models
    ├── tables.py        # Table models
    └── tasks.py         # Task models
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
- Inspired by the Confluence Storage Format specification