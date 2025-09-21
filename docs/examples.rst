Examples
========

This section provides comprehensive examples of using the Confluence Content Parser for common tasks.

Basic Parsing and Text Extraction
---------------------------------

This example demonstrates the fundamental parsing capabilities and text extraction:

.. literalinclude:: ../examples/basic_usage.py
   :language: python
   :caption: Basic Usage Example
   :name: basic-usage

Output Analysis
~~~~~~~~~~~~~~

When you run the basic example, you'll see:

1. **Document Text**: Clean, formatted text with proper spacing
2. **Element Extraction**: Specific element types found and processed
3. **Statistics**: Overview of document structure
4. **Diagnostics**: Any parsing issues encountered

Advanced Content Processing
---------------------------

Working with Complex Layouts
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from confluence_content_parser import ConfluenceParser
   from confluence_content_parser import LayoutElement, LayoutSection, LayoutCell

   # Complex layout content
   layout_content = """
   <ac:layout>
       <ac:layout-section ac:type="two_equal">
           <ac:layout-cell>
               <h2>Left Column</h2>
               <p>Content for the left side.</p>
           </ac:layout-cell>
           <ac:layout-cell>
               <h2>Right Column</h2>
               <p>Content for the right side.</p>
           </ac:layout-cell>
       </ac:layout-section>
   </ac:layout>
   """

   parser = ConfluenceParser()
   document = parser.parse(layout_content)

   # Find layout structure
   layouts = document.find_all(LayoutElement)
   for layout in layouts:
       sections = layout.find_all(LayoutSection)
       for section in sections:
           print(f"Section type: {section.section_type.value}")
           cells = section.find_all(LayoutCell)
           print(f"Number of cells: {len(cells)}")

Processing Macros and Special Content
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from confluence_content_parser import ConfluenceParser
   from confluence_content_parser import PanelMacro, CodeMacro, ExpandMacro

   macro_content = """
   <ac:structured-macro ac:name="info">
       <ac:rich-text-body>
           <p>This is important information.</p>
       </ac:rich-text-body>
   </ac:structured-macro>

   <ac:structured-macro ac:name="code">
       <ac:parameter ac:name="language">python</ac:parameter>
       <ac:plain-text-body>
   def hello_world():
       print("Hello, World!")
       </ac:plain-text-body>
   </ac:structured-macro>

   <ac:structured-macro ac:name="expand">
       <ac:parameter ac:name="title">Click to expand</ac:parameter>
       <ac:rich-text-body>
           <p>Hidden content here.</p>
       </ac:rich-text-body>
   </ac:structured-macro>
   """

   parser = ConfluenceParser()
   document = parser.parse(macro_content)

   # Process different macro types
   panels = document.find_all(PanelMacro)
   for panel in panels:
       print(f"Panel type: {panel.type.value}")
       print(f"Content: {panel.to_text()}")

   code_blocks = document.find_all(CodeMacro)
   for code in code_blocks:
       print(f"Language: {code.language}")
       print(f"Code: {code.code}")

   expand_sections = document.find_all(ExpandMacro)
   for expand in expand_sections:
       print(f"Title: {expand.title}")
       print(f"Content: {expand.to_text()}")

Table Processing
~~~~~~~~~~~~~~~

.. code-block:: python

   from confluence_content_parser import ConfluenceParser
   from confluence_content_parser import Table, TableRow, TableCell

   table_content = """
   <table>
       <tr>
           <th>Name</th>
           <th>Role</th>
           <th>Department</th>
       </tr>
       <tr>
           <td>John Doe</td>
           <td>Developer</td>
           <td>Engineering</td>
       </tr>
       <tr>
           <td>Jane Smith</td>
           <td>Designer</td>
           <td>UX</td>
       </tr>
   </table>
   """

   parser = ConfluenceParser()
   document = parser.parse(table_content)

   # Extract table data
   tables = document.find_all(Table)
   for table in tables:
       rows = table.find_all(TableRow)

       for i, row in enumerate(rows):
           cells = row.find_all(TableCell)
           cell_data = []

           for cell in cells:
               cell_text = cell.to_text()
               if cell.is_header:
                   cell_text = f"**{cell_text}**"  # Mark headers
               cell_data.append(cell_text)

           print(f"Row {i + 1}: {' | '.join(cell_data)}")

Task List Processing
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from confluence_content_parser import ConfluenceParser
   from confluence_content_parser import ListElement, ListItem, ListType, TaskListItemStatus

   task_content = """
   <ac:task-list>
       <ac:task>
           <ac:task-id>1</ac:task-id>
           <ac:task-status>complete</ac:task-status>
           <ac:task-body>Complete project setup</ac:task-body>
       </ac:task>
       <ac:task>
           <ac:task-id>2</ac:task-id>
           <ac:task-status>incomplete</ac:task-status>
           <ac:task-body>Write documentation</ac:task-body>
       </ac:task>
   </ac:task-list>
   """

   parser = ConfluenceParser()
   document = parser.parse(task_content)

   # Process task lists
   lists = document.find_all(ListElement)
   task_lists = [lst for lst in lists if lst.type == ListType.TASK]

   for task_list in task_lists:
       print("Task List:")
       items = task_list.find_all(ListItem)

       for item in items:
           status_symbol = "✓" if item.status == TaskListItemStatus.COMPLETE else "○"
           task_text = item.to_text()
           print(f"  {status_symbol} {task_text}")

Error Handling and Diagnostics
------------------------------

.. literalinclude:: ../examples/diagnostics_usage.py
   :language: python
   :caption: Diagnostics and Error Handling
   :name: diagnostics-usage

Custom Content Analysis
----------------------

Document Statistics
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from confluence_content_parser import ConfluenceParser
   from confluence_content_parser import (
       HeadingElement, LinkElement, Image, Table,
       ListElement, PanelMacro, CodeMacro
   )

   def analyze_document(content):
       """Analyze a Confluence document and return statistics."""
       parser = ConfluenceParser()
       document = parser.parse(content)

       stats = {
           'total_nodes': len(list(document.walk())),
           'headings': len(document.find_all(HeadingElement)),
           'links': len(document.find_all(LinkElement)),
           'images': len(document.find_all(Image)),
           'tables': len(document.find_all(Table)),
           'lists': len(document.find_all(ListElement)),
           'panels': len(document.find_all(PanelMacro)),
           'code_blocks': len(document.find_all(CodeMacro)),
           'text_length': len(document.text),
           'diagnostics': document.metadata.get('diagnostics', [])
       }

       return stats

   # Usage
   content = """<h1>Sample</h1><p>Text with <strong>formatting</strong></p>"""
   stats = analyze_document(content)

   print("Document Analysis:")
   for key, value in stats.items():
       if key != 'diagnostics':
           print(f"  {key.replace('_', ' ').title()}: {value}")

   if stats['diagnostics']:
       print("  Parsing Issues:")
       for diagnostic in stats['diagnostics']:
           print(f"    - {diagnostic}")

Content Search and Filtering
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from confluence_content_parser import ConfluenceParser
   from confluence_content_parser import HeadingElement, Text, LinkElement

   def search_content(document, search_term):
       """Search for content containing a specific term."""
       matching_nodes = []

       for node in document.walk():
           text_content = node.to_text().lower()
           if search_term.lower() in text_content:
               matching_nodes.append({
                   'type': type(node).__name__,
                   'content': node.to_text()[:100] + '...' if len(node.to_text()) > 100 else node.to_text(),
                   'node': node
               })

       return matching_nodes

   def find_external_links(document):
       """Find all external links in the document."""
       from confluence_content_parser import LinkType

       links = document.find_all(LinkElement)
       external_links = []

       for link in links:
           if link.type == LinkType.EXTERNAL and link.href:
               external_links.append({
                   'url': link.href,
                   'text': link.to_text(),
                   'context': link.to_text()
               })

       return external_links

   # Usage example
   parser = ConfluenceParser()
   document = parser.parse(confluence_content)

   # Search for specific content
   api_references = search_content(document, 'API')
   print(f"Found {len(api_references)} API references")

   # Find external links
   external_links = find_external_links(document)
   for link in external_links:
       print(f"External link: {link['url']} ({link['text']})")

Content Transformation
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from confluence_content_parser import ConfluenceParser
   from confluence_content_parser import HeadingElement, CodeMacro, PanelMacro

   def convert_to_markdown(document):
       """Convert a Confluence document to Markdown format."""
       markdown_lines = []

       for node in document.walk():
           if isinstance(node, HeadingElement):
               level = int(node.type.value[1])  # Extract number from h1, h2, etc.
               prefix = '#' * level
               markdown_lines.append(f"{prefix} {node.to_text()}")

           elif isinstance(node, CodeMacro):
               language = node.language or ''
               markdown_lines.append(f"```{language}")
               markdown_lines.append(node.code)
               markdown_lines.append("```")

           elif isinstance(node, PanelMacro):
               panel_type = node.type.value.upper()
               content = ' '.join(child.to_text() for child in node.children)
               markdown_lines.append(f"> **{panel_type}**: {content}")

       return '\n\n'.join(markdown_lines)

   # Usage
   parser = ConfluenceParser()
   document = parser.parse(confluence_content)
   markdown = convert_to_markdown(document)
   print(markdown)

Performance Optimization
------------------------

Streaming Large Documents
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from confluence_content_parser import ConfluenceParser
   from confluence_content_parser import HeadingElement

   def process_large_document(xml_content, chunk_size=1000):
       """Process large documents in chunks to manage memory."""
       parser = ConfluenceParser()
       document = parser.parse(xml_content)

       # Process headings only for outline
       headings = document.find_all(HeadingElement)
       outline = []

       for heading in headings:
           level = int(heading.type.value[1])
           text = heading.to_text()
           outline.append(f"{'  ' * (level - 1)}- {text}")

       return outline

   def extract_text_efficiently(document):
       """Extract text without loading entire tree into memory."""
       text_chunks = []
       current_chunk = []
       current_size = 0
       max_chunk_size = 1000

       for node in document.walk():
           text = node.to_text()
           if text.strip():
               current_chunk.append(text)
               current_size += len(text)

               if current_size >= max_chunk_size:
                   text_chunks.append(' '.join(current_chunk))
                   current_chunk = []
                   current_size = 0

       if current_chunk:
           text_chunks.append(' '.join(current_chunk))

       return text_chunks

Integration Examples
-------------------

Document Validation
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from confluence_content_parser import ConfluenceParser, ParsingError

   def validate_confluence_document(xml_content):
       """Validate and report on Confluence document quality."""
       parser = ConfluenceParser(raise_on_finish=False)

       try:
           document = parser.parse(xml_content)

           validation_results = {
               'valid': True,
               'warnings': document.metadata.get('diagnostics', []),
               'statistics': {
                   'total_nodes': len(list(document.walk())),
                   'text_length': len(document.text)
               }
           }

           return validation_results

       except Exception as e:
           return {
               'valid': False,
               'error': str(e),
               'warnings': [],
               'statistics': {}
           }

   # Usage
   validation = validate_confluence_document(xml_content)
   if validation['valid']:
       print("Document is valid")
       if validation['warnings']:
           print(f"Warnings: {validation['warnings']}")
   else:
       print(f"Validation failed: {validation['error']}")

Batch Processing
~~~~~~~~~~~~~~~

.. code-block:: python

   from confluence_content_parser import ConfluenceParser
   import concurrent.futures
   import os

   def process_single_file(file_path):
       """Process a single Confluence XML file."""
       try:
           with open(file_path, 'r', encoding='utf-8') as f:
               content = f.read()

           parser = ConfluenceParser(raise_on_finish=False)
           document = parser.parse(content)

           return {
               'file': file_path,
               'success': True,
               'text_length': len(document.text),
               'diagnostics': document.metadata.get('diagnostics', [])
           }

       except Exception as e:
           return {
               'file': file_path,
               'success': False,
               'error': str(e)
           }

   def batch_process_files(file_paths, max_workers=4):
       """Process multiple Confluence files in parallel."""
       results = []

       with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
           future_to_file = {
               executor.submit(process_single_file, file_path): file_path
               for file_path in file_paths
           }

           for future in concurrent.futures.as_completed(future_to_file):
               result = future.result()
               results.append(result)

       return results

   # Usage
   xml_files = ['doc1.xml', 'doc2.xml', 'doc3.xml']
   results = batch_process_files(xml_files)

   for result in results:
       if result['success']:
           print(f"Processed {result['file']}: {result['text_length']} chars")
       else:
           print(f"Failed {result['file']}: {result['error']}")

Testing Patterns
----------------

Unit Testing with Parser
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import unittest
   from confluence_content_parser import ConfluenceParser
   from confluence_content_parser import HeadingElement, PanelMacro

   class TestConfluenceParser(unittest.TestCase):

       def setUp(self):
           self.parser = ConfluenceParser()

       def test_heading_parsing(self):
           """Test that headings are parsed correctly."""
           content = "<h1>Main Title</h1><h2>Subtitle</h2>"
           document = self.parser.parse(content)

           headings = document.find_all(HeadingElement)
           self.assertEqual(len(headings), 2)
           self.assertEqual(headings[0].to_text(), "Main Title")
           self.assertEqual(headings[1].to_text(), "Subtitle")

       def test_panel_macro(self):
           """Test panel macro parsing."""
           content = '''
           <ac:structured-macro ac:name="info">
               <ac:rich-text-body>
                   <p>Important information</p>
               </ac:rich-text-body>
           </ac:structured-macro>
           '''
           document = self.parser.parse(content)

           panels = document.find_all(PanelMacro)
           self.assertEqual(len(panels), 1)
           self.assertIn("Important information", panels[0].to_text())

       def test_error_handling(self):
           """Test error handling for malformed content."""
           malformed_content = "<h1>Unclosed heading"

           # Should not raise exception with raise_on_finish=False
           parser = ConfluenceParser(raise_on_finish=False)
           document = parser.parse(malformed_content)

           # Check diagnostics
           diagnostics = document.metadata.get('diagnostics', [])
           self.assertIsInstance(diagnostics, list)

   if __name__ == '__main__':
       unittest.main()

See Also
--------

* :doc:`user_guide` - Comprehensive guide to using the library
* :doc:`api_reference` - Complete API documentation
* `examples/ directory <https://github.com/Unificon/confluence-content-parser/tree/main/examples>`_ - Additional examples in the repository