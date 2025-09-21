Confluence Content Parser Documentation
=========================================

A Python library for parsing Atlassian Confluence storage format XML into a structured document tree.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   quickstart
   user_guide
   api_reference
   examples

Overview
--------

The Confluence Content Parser is a comprehensive Python library designed to parse Confluence storage format XML documents into a structured, navigable document tree. It converts Confluence's complex XML structure into Python objects that are easy to work with programmatically.

Key Features
------------

* **Complete Element Support**: Handles all major Confluence elements including macros, layouts, tables, lists, and more
* **Type Safety**: Built with Pydantic for robust data validation and type hints
* **Text Extraction**: Intelligent text extraction with proper formatting and structure preservation
* **Flexible Navigation**: Multiple ways to traverse and search the document tree
* **Error Handling**: Comprehensive error diagnostics for malformed content

Quick Example
-------------

.. code-block:: python

   from confluence_content_parser import ConfluenceParser

   # Parse Confluence XML content
   parser = ConfluenceParser()
   document = parser.parse(confluence_xml)

   # Extract plain text
   text_content = document.text

   # Find specific elements
   headings = document.find_all(HeadingElement)

   # Navigate the document tree
   for node in document.walk():
       print(f"Found {type(node).__name__}: {node.to_text()}")

Architecture
------------

The library is built around three main components:

:class:`~confluence_content_parser.document.ConfluenceDocument`
   The main document interface providing high-level access to parsed content.

:class:`~confluence_content_parser.nodes.Node`
   A comprehensive hierarchy of node classes representing different Confluence elements.

:class:`~confluence_content_parser.parser.ConfluenceParser`
   The XML parser that converts Confluence storage format into the node tree.

Supported Elements
------------------

The parser supports a wide range of Confluence elements:

**Structure Elements**
   * Layouts and layout sections
   * Paragraphs and headings
   * Lists (ordered, unordered, task lists)
   * Tables with complex formatting

**Content Elements**
   * Text formatting (bold, italic, underline, etc.)
   * Links (internal and external)
   * Images with captions
   * Code blocks with syntax highlighting

**Macros**
   * Panel macros (info, warning, error, etc.)
   * Expand/collapse sections
   * Table of contents
   * JIRA integration
   * Include macros
   * And many more...

License
-------

This project is licensed under the Apache License 2.0.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`