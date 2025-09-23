Quick Start Guide
=================

This guide will get you up and running with the Confluence Content Parser in just a few minutes.

Basic Usage
-----------

The most common use case is parsing Confluence XML content and extracting text:

.. code-block:: python

   from confluence_content_parser import ConfluenceParser

   # Sample Confluence XML (simplified)
   confluence_xml = """
   <p>Hello <strong>world</strong>!</p>
   <h1>Main Heading</h1>
   <p>Some paragraph text with <em>emphasis</em>.</p>
   """

   # Create parser and parse content
   parser = ConfluenceParser()
   document = parser.parse(confluence_xml)

   # Extract all text content
   print(document.text)
   # Output: Hello world!
   #
   # Main Heading
   #
   # Some paragraph text with emphasis.

Finding Specific Elements
------------------------

You can search for specific types of content within the document:

.. code-block:: python

   from confluence_content_parser.nodes import HeadingElement, TextEffectElement

   # Find all headings
   headings = document.find_all(HeadingElement)
   for heading in headings:
       print(f"Heading: {heading.to_text()}")

   # Find multiple types at once
   headings, bold_elements = document.find_all(HeadingElement, TextEffectElement)
   print(f"Found {len(headings)} headings and {len(bold_elements)} text effects")

   # Find all bold text
   for element in bold_elements:
       if element.type.value == 'strong':
           print(f"Bold text: {element.to_text()}")

Walking the Document Tree
------------------------

For more detailed analysis, you can walk through every node in the document:

.. code-block:: python

   # Walk through all nodes
   for node in document.walk():
       node_type = type(node).__name__
       text_content = node.to_text()
       print(f"{node_type}: {text_content}")

Working with Complex Content
---------------------------

The parser handles complex Confluence elements like macros, tables, and layouts:

.. code-block:: python

   # Sample with macro content
   complex_xml = """
   <ac:structured-macro ac:name="info">
       <ac:rich-text-body>
           <p>This is an info panel with <strong>important</strong> information.</p>
       </ac:rich-text-body>
   </ac:structured-macro>
   """

   document = parser.parse(complex_xml)
   print(document.text)
   # Output: ℹ️ INFO: This is an info panel with important information.

Error Handling
--------------

The parser provides diagnostic information when encountering issues:

.. code-block:: python

   # Parse with error handling
   try:
       document = parser.parse(malformed_xml)
   except ParsingError as e:
       print(f"Parsing failed: {e}")
       print("Diagnostics:", e.diagnostics)

   # Or check diagnostics after parsing
   parser = ConfluenceParser(raise_on_finish=False)
   document = parser.parse(xml_content)

   if parser.diagnostics:
       print("Warnings:", parser.diagnostics)

Next Steps
----------

* Read the :doc:`user_guide` for detailed information about node types and advanced usage
* Check the :doc:`api_reference` for complete API documentation
* Browse :doc:`examples` for real-world usage patterns