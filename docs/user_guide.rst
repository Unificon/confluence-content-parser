User Guide
==========

This comprehensive guide covers all aspects of using the Confluence Content Parser.

Understanding the Document Model
-------------------------------

The Confluence Content Parser converts XML into a tree structure of Python objects. At the root is a :class:`~confluence_content_parser.document.ConfluenceDocument` which contains a tree of :class:`~confluence_content_parser.nodes.Node` objects.

Document Structure
~~~~~~~~~~~~~~~~~

.. code-block:: python

   document = parser.parse(xml_content)

   # Access the root node
   root_node = document.root

   # Get metadata (including parsing diagnostics)
   metadata = document.metadata

   # Extract all text with proper formatting
   full_text = document.text

Node Hierarchy
~~~~~~~~~~~~~

All content elements inherit from the base :class:`~confluence_content_parser.nodes.Node` class:

* **Container Elements**: Can contain child nodes (paragraphs, headings, lists)
* **Leaf Elements**: Contain only text or specific data (images, emoticons, timestamps)
* **Block Elements**: Render as separate blocks (headings, paragraphs, tables)
* **Inline Elements**: Render within text flow (bold, italic, links)

Working with Different Content Types
-----------------------------------

Text Content
~~~~~~~~~~~

Basic text elements and formatting:

.. code-block:: python

   from confluence_content_parser.nodes import (
       TextEffectElement, TextEffectType,
       HeadingElement, HeadingType
   )

   # Find all bold text
   bold_elements = document.find_all(TextEffectElement)
   for element in bold_elements:
       if element.type == TextEffectType.STRONG:
           print(f"Bold: {element.to_text()}")

   # Find headings by level
   headings = document.find_all(HeadingElement)
   h1_headings = [h for h in headings if h.type == HeadingType.H1]

Lists and Task Lists
~~~~~~~~~~~~~~~~~~

Working with different list types:

.. code-block:: python

   from confluence_content_parser.nodes import (
       ListElement, ListType, ListItem,
       TaskListItemStatus
   )

   # Find all lists
   lists = document.find_all(ListElement)

   for list_elem in lists:
       if list_elem.type == ListType.TASK:
           # Process task list
           for item in list_elem.children:
               if isinstance(item, ListItem):
                   status = "✓" if item.status == TaskListItemStatus.COMPLETE else "○"
                   print(f"{status} {item.to_text()}")

Tables
~~~~~~

Extracting table data:

.. code-block:: python

   from confluence_content_parser.nodes import Table, TableRow, TableCell

   tables = document.find_all(Table)
   for table in tables:
       for row in table.find_all(TableRow):
           cells = row.find_all(TableCell)
           row_data = [cell.to_text() for cell in cells]
           print(" | ".join(row_data))

Links and References
~~~~~~~~~~~~~~~~~~

Handling different link types:

.. code-block:: python

   from confluence_content_parser.nodes import LinkElement, LinkType

   links = document.find_all(LinkElement)
   for link in links:
       if link.type == LinkType.EXTERNAL:
           print(f"External link: {link.href} -> {link.to_text()}")
       elif link.type == LinkType.PAGE:
           print(f"Page link: {link.to_text()}")

Images and Media
~~~~~~~~~~~~~~~

Working with images and attachments:

.. code-block:: python

   from confluence_content_parser.nodes import Image

   images = document.find_all(Image)
   for image in images:
       print(f"Image: {image.alt or image.filename}")
       if image.children:  # Caption content
           caption = " ".join(child.to_text() for child in image.children)
           print(f"Caption: {caption}")

Macros and Special Elements
~~~~~~~~~~~~~~~~~~~~~~~~~

Confluence macros are converted to specific node types:

.. code-block:: python

   from confluence_content_parser.nodes import (
       PanelMacro, PanelMacroType,
       CodeMacro, ExpandMacro
   )

   # Info panels, warnings, etc.
   panels = document.find_all(PanelMacro)
   for panel in panels:
       panel_type = panel.type.value
       content = panel.to_text()
       print(f"{panel_type.upper()}: {content}")

   # Code blocks
   code_blocks = document.find_all(CodeMacro)
   for code in code_blocks:
       language = code.language or "text"
       print(f"Code ({language}):")
       print(code.code)

Advanced Navigation
------------------

Walking the Tree
~~~~~~~~~~~~~~~

There are several ways to traverse the document:

.. code-block:: python

   # Walk all nodes depth-first
   for node in document.walk():
       print(f"Processing {type(node).__name__}")

   # Get only direct children of root
   if document.root:
       for child in document.root.get_children():
           print(f"Top-level: {type(child).__name__}")

   # Find all nodes (equivalent to walk but returns list)
   all_nodes = document.find_all()

Filtering and Searching
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Find by node type
   headings = document.find_all(HeadingElement)

   # Find by multiple criteria using custom logic
   def is_important_content(node):
       if isinstance(node, PanelMacro):
           return node.type in [PanelMacroType.WARNING, PanelMacroType.ERROR]
       elif isinstance(node, HeadingElement):
           return node.type in [HeadingType.H1, HeadingType.H2]
       return False

   important_nodes = [node for node in document.walk() if is_important_content(node)]

Text Extraction Strategies
-------------------------

The library provides several ways to extract text:

Complete Document Text
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Get all text with proper paragraph breaks
   full_text = document.text

   # This preserves the document structure with double newlines
   # between block elements

Node-Specific Text
~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Get text from specific nodes
   for heading in document.find_all(HeadingElement):
       heading_text = heading.to_text()
       print(f"Heading: {heading_text}")

Custom Text Extraction
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   def extract_readable_text(node):
       """Extract text with custom formatting rules."""
       if isinstance(node, HeadingElement):
           level = int(node.type.value[1])  # h1 -> 1, h2 -> 2, etc.
           prefix = "#" * level
           return f"{prefix} {node.to_text()}"
       elif isinstance(node, PanelMacro):
           return f"[{node.type.value.upper()}] {' '.join(child.to_text() for child in node.children)}"
       else:
           return node.to_text()

   for node in document.walk():
       if node.to_text().strip():  # Only nodes with content
           print(extract_readable_text(node))

Error Handling and Diagnostics
-----------------------------

Parsing Errors
~~~~~~~~~~~~~

.. code-block:: python

   from confluence_content_parser.parser import ParsingError

   try:
       document = parser.parse(xml_content)
   except ParsingError as e:
       print(f"Failed to parse: {e}")
       for diagnostic in e.diagnostics:
           print(f"  - {diagnostic}")

Diagnostic Information
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Parse without raising errors
   parser = ConfluenceParser(raise_on_finish=False)
   document = parser.parse(xml_content)

   # Check for warnings and unknown elements
   if parser.diagnostics:
       for diagnostic in parser.diagnostics:
           if diagnostic.startswith("unknown_element:"):
               element_name = diagnostic.split(":", 1)[1]
               print(f"Unknown element encountered: {element_name}")
           elif diagnostic.startswith("unknown_macro:"):
               macro_name = diagnostic.split(":", 1)[1]
               print(f"Unknown macro encountered: {macro_name}")

Performance Considerations
-------------------------

Large Documents
~~~~~~~~~~~~~~

For large documents, consider these strategies:

.. code-block:: python

   # Stream processing - find specific content without loading everything
   def find_headings_only(xml_content):
       parser = ConfluenceParser()
       document = parser.parse(xml_content)
       return document.find_all(HeadingElement)

   # Memory-efficient text extraction
   def extract_text_chunks(document, chunk_size=1000):
       current_chunk = []
       current_length = 0

       for node in document.walk():
           text = node.to_text()
           if text.strip():
               current_chunk.append(text)
               current_length += len(text)

               if current_length >= chunk_size:
                   yield " ".join(current_chunk)
                   current_chunk = []
                   current_length = 0

       if current_chunk:
           yield " ".join(current_chunk)

Best Practices
-------------

1. **Always handle parsing errors** when working with user-provided content
2. **Use type checking** to ensure you're working with the expected node types
3. **Check for empty content** before processing text
4. **Leverage the node hierarchy** to understand content structure
5. **Use find_all() for specific searches** rather than walking the entire tree
6. **Consider performance** when processing large documents

.. code-block:: python

   # Good: Specific search
   code_blocks = document.find_all(CodeMacro)

   # Less efficient: Walking entire tree
   code_blocks = [node for node in document.walk() if isinstance(node, CodeMacro)]