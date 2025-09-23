API Reference
=============

This section provides detailed documentation for all classes and methods in the Confluence Content Parser.

Core Classes
-----------

ConfluenceDocument
~~~~~~~~~~~~~~~~~

.. autoclass:: confluence_content_parser.document.ConfluenceDocument
   :members:
   :show-inheritance:

   The main document class that represents a parsed Confluence document.

   **Properties:**

   .. autoattribute:: confluence_content_parser.document.ConfluenceDocument.root
      :annotation: Node | None

      The root node of the document tree. May be None for empty documents.

   .. autoattribute:: confluence_content_parser.document.ConfluenceDocument.metadata
      :annotation: dict[str, Any]

      Document metadata including parsing diagnostics.

   .. autoattribute:: confluence_content_parser.document.ConfluenceDocument.text
      :annotation: str

      All text content from the document with proper line breaks.

   **Methods:**

   .. automethod:: confluence_content_parser.document.ConfluenceDocument.find_all

      Find nodes by type with support for multiple types in a single call.

      **Multiple Type Search:**

      The ``find_all`` method supports searching for multiple node types simultaneously:

      .. code-block:: python

         # Single type
         headings = document.find_all(HeadingElement)

         # Multiple types (up to 5 with full type inference)
         headings, panels, images = document.find_all(HeadingElement, PanelMacro, Image)

      **Type Safety Limitations:**

      Due to current limitations in Python's type system (specifically with TypeVarTuple 
      transformations), full type inference is supported for up to 5 node types. Beyond 
      5 types, the method still works correctly at runtime but type checkers will fall 
      back to more general typing.

      .. code-block:: python

         # Full type inference (recommended)
         headings, panels, images, tables, links = document.find_all(HeadingElement, PanelMacro, 
                                           Image, Table, LinkElement)

         # Still works, but with general typing beyond 5 types
         headings, panels, images, tables, links, codes = document.find_all(HeadingElement, PanelMacro, Image, 
                                   Table, LinkElement, CodeMacro)

   .. automethod:: confluence_content_parser.document.ConfluenceDocument.walk

ConfluenceParser
~~~~~~~~~~~~~~~

.. autoclass:: confluence_content_parser.parser.ConfluenceParser
   :members:
   :show-inheritance:

   The main parser class for converting Confluence storage format XML to document trees.

   **Constructor:**

   .. automethod:: confluence_content_parser.parser.ConfluenceParser.__init__

   **Methods:**

   .. automethod:: confluence_content_parser.parser.ConfluenceParser.parse

ParsingError
~~~~~~~~~~~

.. autoclass:: confluence_content_parser.parser.ParsingError
   :members:
   :show-inheritance:

   Exception raised when parsing fails with diagnostics.

Base Node Classes
----------------

Node
~~~~

.. autoclass:: confluence_content_parser.nodes.Node
   :members:
   :show-inheritance:

   Base class for all content nodes in the Confluence document tree.

   **Properties:**

   .. autoattribute:: confluence_content_parser.nodes.Node.is_block_level
      :annotation: bool

      Whether this node renders as a block-level element.

   **Methods:**

   .. automethod:: confluence_content_parser.nodes.Node.walk

   .. automethod:: confluence_content_parser.nodes.Node.get_children

   .. automethod:: confluence_content_parser.nodes.Node.to_text

   .. automethod:: confluence_content_parser.nodes.Node.find_all

      Find nodes by type with support for multiple types in a single call.
      See :meth:`confluence_content_parser.document.ConfluenceDocument.find_all` 
      for detailed documentation on multiple type search and type safety limitations.

ContainerElement
~~~~~~~~~~~~~~~

.. autoclass:: confluence_content_parser.nodes.ContainerElement
   :members:
   :show-inheritance:

   Base class for container elements that can contain child nodes.

   **Properties:**

   .. autoattribute:: confluence_content_parser.nodes.ContainerElement.children
      :annotation: list[Node]

      List of child nodes.

   .. autoattribute:: confluence_content_parser.nodes.ContainerElement.styles
      :annotation: dict[str, str]

      CSS styles applied to this element.

Text and Formatting Nodes
-------------------------

Text
~~~~

.. autoclass:: confluence_content_parser.nodes.Text
   :members:
   :show-inheritance:

   A node containing plain text content.

   **Properties:**

   .. autoattribute:: confluence_content_parser.nodes.Text.text
      :annotation: str

      The text content.

TextEffectElement
~~~~~~~~~~~~~~~~

.. autoclass:: confluence_content_parser.nodes.TextEffectElement
   :members:
   :show-inheritance:

   Inline formatting elements like bold, italic, etc.

   **Properties:**

   .. autoattribute:: confluence_content_parser.nodes.TextEffectElement.type
      :annotation: TextEffectType

      The type of text effect.

TextEffectType
~~~~~~~~~~~~~

.. autoclass:: confluence_content_parser.nodes.TextEffectType
   :members:
   :show-inheritance:

   Enumeration of text effect types.

   **Values:**

   * ``STRONG`` - Bold text
   * ``EMPHASIS`` - Italic text
   * ``UNDERLINE`` - Underlined text
   * ``STRIKETHROUGH`` - Strikethrough text
   * ``MONOSPACE`` - Monospace/code text
   * ``SUBSCRIPT`` - Subscript text
   * ``SUPERSCRIPT`` - Superscript text
   * ``BLOCKQUOTE`` - Block quotation
   * ``SPAN`` - Generic inline container

TextBreakElement
~~~~~~~~~~~~~~~

.. autoclass:: confluence_content_parser.nodes.TextBreakElement
   :members:
   :show-inheritance:

   Text break elements like paragraphs, line breaks, and horizontal rules.

   **Properties:**

   .. autoattribute:: confluence_content_parser.nodes.TextBreakElement.type
      :annotation: TextBreakType

      The type of text break.

TextBreakType
~~~~~~~~~~~~

.. autoclass:: confluence_content_parser.nodes.TextBreakType
   :members:
   :show-inheritance:

   Enumeration of text break types.

   **Values:**

   * ``PARAGRAPH`` - Paragraph element
   * ``LINE_BREAK`` - Line break element
   * ``HORIZONTAL_RULE`` - Horizontal rule element

Structure Nodes
--------------

HeadingElement
~~~~~~~~~~~~~

.. autoclass:: confluence_content_parser.nodes.HeadingElement
   :members:
   :show-inheritance:

   Heading elements (h1-h6).

   **Properties:**

   .. autoattribute:: confluence_content_parser.nodes.HeadingElement.type
      :annotation: HeadingType

      The heading level.

HeadingType
~~~~~~~~~~

.. autoclass:: confluence_content_parser.nodes.HeadingType
   :members:
   :show-inheritance:

   Enumeration of heading types.

   **Values:**

   * ``H1`` - Level 1 heading
   * ``H2`` - Level 2 heading
   * ``H3`` - Level 3 heading
   * ``H4`` - Level 4 heading
   * ``H5`` - Level 5 heading
   * ``H6`` - Level 6 heading

List Nodes
----------

ListElement
~~~~~~~~~~

.. autoclass:: confluence_content_parser.nodes.ListElement
   :members:
   :show-inheritance:

   List elements (ordered, unordered, task lists).

   **Properties:**

   .. autoattribute:: confluence_content_parser.nodes.ListElement.type
      :annotation: ListType

      The type of list.

   .. autoattribute:: confluence_content_parser.nodes.ListElement.start
      :annotation: int | None

      Starting number for ordered lists.

ListType
~~~~~~~~

.. autoclass:: confluence_content_parser.nodes.ListType
   :members:
   :show-inheritance:

   Enumeration of list types.

   **Values:**

   * ``UNORDERED`` - Unordered/bulleted list
   * ``ORDERED`` - Ordered/numbered list
   * ``TASK`` - Task list with checkboxes

ListItem
~~~~~~~~

.. autoclass:: confluence_content_parser.nodes.ListItem
   :members:
   :show-inheritance:

   List item element that can be regular or task item.

   **Properties:**

   .. autoattribute:: confluence_content_parser.nodes.ListItem.task_id
      :annotation: str | None

      Task ID for task list items.

   .. autoattribute:: confluence_content_parser.nodes.ListItem.uuid
      :annotation: str | None

      Unique identifier for task items.

   .. autoattribute:: confluence_content_parser.nodes.ListItem.status
      :annotation: TaskListItemStatus | None

      Completion status for task items.

TaskListItemStatus
~~~~~~~~~~~~~~~~~

.. autoclass:: confluence_content_parser.nodes.TaskListItemStatus
   :members:
   :show-inheritance:

   Enumeration of task list item statuses.

   **Values:**

   * ``COMPLETE`` - Task is completed
   * ``INCOMPLETE`` - Task is not completed

Table Nodes
-----------

Table
~~~~~

.. autoclass:: confluence_content_parser.nodes.Table
   :members:
   :show-inheritance:

   Table element with metadata and rows.

   **Properties:**

   .. autoattribute:: confluence_content_parser.nodes.Table.width
      :annotation: str | None

      Table width specification.

   .. autoattribute:: confluence_content_parser.nodes.Table.layout
      :annotation: str | None

      Table layout type.

   .. autoattribute:: confluence_content_parser.nodes.Table.local_id
      :annotation: str | None

      Local identifier for the table.

   .. autoattribute:: confluence_content_parser.nodes.Table.display_mode
      :annotation: str | None

      Display mode for the table.

TableRow
~~~~~~~~

.. autoclass:: confluence_content_parser.nodes.TableRow
   :members:
   :show-inheritance:

   Table row element.

TableCell
~~~~~~~~~

.. autoclass:: confluence_content_parser.nodes.TableCell
   :members:
   :show-inheritance:

   Table cell element.

   **Properties:**

   .. autoattribute:: confluence_content_parser.nodes.TableCell.is_header
      :annotation: bool

      Whether this is a header cell.

   .. autoattribute:: confluence_content_parser.nodes.TableCell.rowspan
      :annotation: int | None

      Number of rows this cell spans.

   .. autoattribute:: confluence_content_parser.nodes.TableCell.colspan
      :annotation: int | None

      Number of columns this cell spans.

Layout Nodes
-----------

LayoutElement
~~~~~~~~~~~~

.. autoclass:: confluence_content_parser.nodes.LayoutElement
   :members:
   :show-inheritance:

   Page layout container containing sections.

LayoutSection
~~~~~~~~~~~~

.. autoclass:: confluence_content_parser.nodes.LayoutSection
   :members:
   :show-inheritance:

   Layout section (row) containing cells.

   **Properties:**

   .. autoattribute:: confluence_content_parser.nodes.LayoutSection.section_type
      :annotation: LayoutSectionType

      The type of layout section.

   .. autoattribute:: confluence_content_parser.nodes.LayoutSection.breakout_mode
      :annotation: str | None

      Breakout mode for the section.

   .. autoattribute:: confluence_content_parser.nodes.LayoutSection.breakout_width
      :annotation: str | None

      Breakout width specification.

LayoutSectionType
~~~~~~~~~~~~~~~~

.. autoclass:: confluence_content_parser.nodes.LayoutSectionType
   :members:
   :show-inheritance:

   Enumeration of layout section types.

LayoutCell
~~~~~~~~~

.. autoclass:: confluence_content_parser.nodes.LayoutCell
   :members:
   :show-inheritance:

   Layout cell (column) containing content.

Link and Media Nodes
-------------------

LinkElement
~~~~~~~~~~

.. autoclass:: confluence_content_parser.nodes.LinkElement
   :members:
   :show-inheritance:

   Link element for internal and external links.

   **Properties:**

   .. autoattribute:: confluence_content_parser.nodes.LinkElement.type
      :annotation: LinkType

      The type of link.

   .. autoattribute:: confluence_content_parser.nodes.LinkElement.href
      :annotation: str | None

      The link target URL.

   .. autoattribute:: confluence_content_parser.nodes.LinkElement.anchor
      :annotation: str | None

      Anchor name for internal links.

LinkType
~~~~~~~~

.. autoclass:: confluence_content_parser.nodes.LinkType
   :members:
   :show-inheritance:

   Enumeration of link types.

Image
~~~~~

.. autoclass:: confluence_content_parser.nodes.Image
   :members:
   :show-inheritance:

   Image element with metadata and optional caption.

   **Properties:**

   .. autoattribute:: confluence_content_parser.nodes.Image.src
      :annotation: str | None

      Image source URL.

   .. autoattribute:: confluence_content_parser.nodes.Image.alt
      :annotation: str | None

      Alternative text for the image.

   .. autoattribute:: confluence_content_parser.nodes.Image.title
      :annotation: str | None

      Image title.

   .. autoattribute:: confluence_content_parser.nodes.Image.width
      :annotation: str | None

      Image width.

   .. autoattribute:: confluence_content_parser.nodes.Image.height
      :annotation: str | None

      Image height.

Macro Nodes
-----------

PanelMacro
~~~~~~~~~

.. autoclass:: confluence_content_parser.nodes.PanelMacro
   :members:
   :show-inheritance:

   Panel macro for info, warning, and custom panels.

   **Properties:**

   .. autoattribute:: confluence_content_parser.nodes.PanelMacro.type
      :annotation: PanelMacroType

      The type of panel.

   .. autoattribute:: confluence_content_parser.nodes.PanelMacro.bg_color
      :annotation: str | None

      Background color specification.

PanelMacroType
~~~~~~~~~~~~~

.. autoclass:: confluence_content_parser.nodes.PanelMacroType
   :members:
   :show-inheritance:

   Enumeration of panel macro types.

CodeMacro
~~~~~~~~

.. autoclass:: confluence_content_parser.nodes.CodeMacro
   :members:
   :show-inheritance:

   Code macro for syntax-highlighted code blocks.

   **Properties:**

   .. autoattribute:: confluence_content_parser.nodes.CodeMacro.language
      :annotation: str | None

      Programming language for syntax highlighting.

   .. autoattribute:: confluence_content_parser.nodes.CodeMacro.code
      :annotation: str

      The code content.

StatusMacro
~~~~~~~~~~

.. autoclass:: confluence_content_parser.nodes.StatusMacro
   :members:
   :show-inheritance:

   Status macro for displaying status indicators.

   **Properties:**

   .. autoattribute:: confluence_content_parser.nodes.StatusMacro.title
      :annotation: str | None

      Status text.

   .. autoattribute:: confluence_content_parser.nodes.StatusMacro.colour
      :annotation: str | None

      Status color.

Other Macro Nodes
----------------

ExpandMacro
~~~~~~~~~~

.. autoclass:: confluence_content_parser.nodes.ExpandMacro
   :members:
   :show-inheritance:

   Expand/collapse macro for collapsible content sections.

DetailsMacro
~~~~~~~~~~~

.. autoclass:: confluence_content_parser.nodes.DetailsMacro
   :members:
   :show-inheritance:

   Details macro for collapsible content sections.

TocMacro
~~~~~~~

.. autoclass:: confluence_content_parser.nodes.TocMacro
   :members:
   :show-inheritance:

   Table of contents macro.

JiraMacro
~~~~~~~~

.. autoclass:: confluence_content_parser.nodes.JiraMacro
   :members:
   :show-inheritance:

   JIRA issue integration macro.

IncludeMacro
~~~~~~~~~~~

.. autoclass:: confluence_content_parser.nodes.IncludeMacro
   :members:
   :show-inheritance:

   Include macro for including other pages.

Utility Nodes
------------

Fragment
~~~~~~~~

.. autoclass:: confluence_content_parser.nodes.Fragment
   :members:
   :show-inheritance:

   Neutral container for multiple top-level nodes.

Emoticon
~~~~~~~~

.. autoclass:: confluence_content_parser.nodes.Emoticon
   :members:
   :show-inheritance:

   Emoticon element for Confluence emoticons and emojis.

Time
~~~~

.. autoclass:: confluence_content_parser.nodes.Time
   :members:
   :show-inheritance:

   Time element with datetime information.

PlaceholderElement
~~~~~~~~~~~~~~~~~

.. autoclass:: confluence_content_parser.nodes.PlaceholderElement
   :members:
   :show-inheritance:

   Placeholder element for dynamic content.

ResourceIdentifier
~~~~~~~~~~~~~~~~~

.. autoclass:: confluence_content_parser.nodes.ResourceIdentifier
   :members:
   :show-inheritance:

   Resource identifier for references to pages, attachments, etc.

Usage Examples
--------------

For practical usage examples, see the :doc:`examples` section and the :doc:`user_guide`.