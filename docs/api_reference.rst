API Reference
=============

This section provides detailed documentation for all classes and methods in the Confluence Content Parser.

Core Classes
------------

ConfluenceDocument
~~~~~~~~~~~~~~~~~~

.. autoclass:: confluence_content_parser.document.ConfluenceDocument
   :show-inheritance:
   :members:
   :no-inherited-members:

ConfluenceParser
~~~~~~~~~~~~~~~~

.. autoclass:: confluence_content_parser.parser.ConfluenceParser
   :show-inheritance:
   :members:
   :no-inherited-members:

ParsingError
~~~~~~~~~~~~

.. autoclass:: confluence_content_parser.parser.ParsingError
   :show-inheritance:
   :members:
   :no-inherited-members:

Base Node Classes
-----------------

Node
~~~~

.. autoclass:: confluence_content_parser.nodes.Node
   :show-inheritance:
   :members:
   :no-inherited-members:

ContainerElement
~~~~~~~~~~~~~~~~

.. autoclass:: confluence_content_parser.nodes.ContainerElement
   :show-inheritance:
   :members:
   :no-inherited-members:

Text and Formatting Nodes
-------------------------

Text
~~~~

.. autoclass:: confluence_content_parser.nodes.Text
   :show-inheritance:
   :members:
   :no-inherited-members:

TextEffectElement
~~~~~~~~~~~~~~~~~

.. autoclass:: confluence_content_parser.nodes.TextEffectElement
   :show-inheritance:
   :members:
   :no-inherited-members:

TextEffectType
~~~~~~~~~~~~~~

.. autoclass:: confluence_content_parser.nodes.TextEffectType
   :show-inheritance:
   :no-members:

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
~~~~~~~~~~~~~~~~

.. autoclass:: confluence_content_parser.nodes.TextBreakElement
   :show-inheritance:
   :members:
   :no-inherited-members:

TextBreakType
~~~~~~~~~~~~~

.. autoclass:: confluence_content_parser.nodes.TextBreakType
   :show-inheritance:
   :no-members:

   Enumeration of text break types.

   **Values:**

   * ``PARAGRAPH`` - Paragraph element
   * ``LINE_BREAK`` - Line break element
   * ``HORIZONTAL_RULE`` - Horizontal rule element

Structure Nodes
---------------

HeadingElement
~~~~~~~~~~~~~~

.. autoclass:: confluence_content_parser.nodes.HeadingElement
   :show-inheritance:
   :members:
   :no-inherited-members:

HeadingType
~~~~~~~~~~~

.. autoclass:: confluence_content_parser.nodes.HeadingType
   :show-inheritance:
   :no-members:

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
~~~~~~~~~~~

.. autoclass:: confluence_content_parser.nodes.ListElement
   :show-inheritance:
   :members:
   :no-inherited-members:

ListType
~~~~~~~~

.. autoclass:: confluence_content_parser.nodes.ListType
   :show-inheritance:
   :no-members:

   Enumeration of list types.

   **Values:**

   * ``UNORDERED`` - Unordered/bulleted list
   * ``ORDERED`` - Ordered/numbered list
   * ``TASK`` - Task list with checkboxes

ListItem
~~~~~~~~

.. autoclass:: confluence_content_parser.nodes.ListItem
   :show-inheritance:
   :members:
   :no-inherited-members:

TaskListItemStatus
~~~~~~~~~~~~~~~~~~

.. autoclass:: confluence_content_parser.nodes.TaskListItemStatus
   :show-inheritance:
   :no-members:

   Enumeration of task list item statuses.

   **Values:**

   * ``COMPLETE`` - Task is completed
   * ``INCOMPLETE`` - Task is not completed

Table Nodes
-----------

Table
~~~~~

.. autoclass:: confluence_content_parser.nodes.Table
   :show-inheritance:
   :members:
   :no-inherited-members:

TableRow
~~~~~~~~

.. autoclass:: confluence_content_parser.nodes.TableRow
   :show-inheritance:
   :members:
   :no-inherited-members:

TableCell
~~~~~~~~~

.. autoclass:: confluence_content_parser.nodes.TableCell
   :show-inheritance:
   :members:
   :no-inherited-members:

Layout Nodes
------------

LayoutElement
~~~~~~~~~~~~~

.. autoclass:: confluence_content_parser.nodes.LayoutElement
   :show-inheritance:
   :members:
   :no-inherited-members:

LayoutSection
~~~~~~~~~~~~~

.. autoclass:: confluence_content_parser.nodes.LayoutSection
   :show-inheritance:
   :members:
   :no-inherited-members:

LayoutSectionType
~~~~~~~~~~~~~~~~~

.. autoclass:: confluence_content_parser.nodes.LayoutSectionType
   :show-inheritance:
   :no-members:

   Enumeration of layout section types.

   **Values:**

   * ``SINGLE`` - Single column layout
   * ``FIXED_WIDTH`` - Fixed width layout
   * ``TWO_EQUAL`` - Two equal columns
   * ``TWO_LEFT_SIDEBAR`` - Two columns with left sidebar
   * ``TWO_RIGHT_SIDEBAR`` - Two columns with right sidebar
   * ``THREE_EQUAL`` - Three equal columns
   * ``THREE_WITH_SIDEBARS`` - Three columns with sidebars
   * ``THREE_LEFT_SIDEBARS`` - Three columns with left sidebars
   * ``THREE_RIGHT_SIDEBARS`` - Three columns with right sidebars
   * ``FOUR_EQUAL`` - Four equal columns
   * ``FIVE_EQUAL`` - Five equal columns

LayoutCell
~~~~~~~~~~

.. autoclass:: confluence_content_parser.nodes.LayoutCell
   :show-inheritance:
   :members:
   :no-inherited-members:

Link and Media Nodes
--------------------

LinkElement
~~~~~~~~~~~

.. autoclass:: confluence_content_parser.nodes.LinkElement
   :show-inheritance:
   :members:
   :no-inherited-members:

LinkType
~~~~~~~~

.. autoclass:: confluence_content_parser.nodes.LinkType
   :show-inheritance:
   :no-members:

   Enumeration of link types.

   **Values:**

   * ``EXTERNAL`` - External link
   * ``MAILTO`` - Email link
   * ``SPACE`` - Space reference
   * ``PAGE`` - Page reference
   * ``BLOG_POST`` - Blog post reference
   * ``USER`` - User reference
   * ``ATTACHMENT`` - Attachment reference
   * ``ANCHOR`` - Anchor reference

Image
~~~~~

.. autoclass:: confluence_content_parser.nodes.Image
   :show-inheritance:
   :members:
   :no-inherited-members:

Macro Nodes
-----------

PanelMacro
~~~~~~~~~~

.. autoclass:: confluence_content_parser.nodes.PanelMacro
   :show-inheritance:
   :members:
   :no-inherited-members:

PanelMacroType
~~~~~~~~~~~~~~

.. autoclass:: confluence_content_parser.nodes.PanelMacroType
   :show-inheritance:
   :no-members:

   Enumeration of panel macro types.

   **Values:**

   * ``PANEL`` - Generic panel
   * ``NOTE`` - Note panel
   * ``SUCCESS`` - Success panel
   * ``WARNING`` - Warning panel
   * ``ERROR`` - Error panel
   * ``INFO`` - Info panel

CodeMacro
~~~~~~~~~

.. autoclass:: confluence_content_parser.nodes.CodeMacro
   :show-inheritance:
   :members:
   :no-inherited-members:

StatusMacro
~~~~~~~~~~~

.. autoclass:: confluence_content_parser.nodes.StatusMacro
   :show-inheritance:
   :members:
   :no-inherited-members:

Other Macro Nodes
-----------------

ExpandMacro
~~~~~~~~~~~

.. autoclass:: confluence_content_parser.nodes.ExpandMacro
   :show-inheritance:
   :members:
   :no-inherited-members:

DetailsMacro
~~~~~~~~~~~~

.. autoclass:: confluence_content_parser.nodes.DetailsMacro
   :show-inheritance:
   :members:
   :no-inherited-members:

TocMacro
~~~~~~~~

.. autoclass:: confluence_content_parser.nodes.TocMacro
   :show-inheritance:
   :members:
   :no-inherited-members:

JiraMacro
~~~~~~~~~

.. autoclass:: confluence_content_parser.nodes.JiraMacro
   :show-inheritance:
   :members:
   :no-inherited-members:

IncludeMacro
~~~~~~~~~~~~

.. autoclass:: confluence_content_parser.nodes.IncludeMacro
   :show-inheritance:
   :members:
   :no-inherited-members:

TasksReportMacro
~~~~~~~~~~~~~~~~

.. autoclass:: confluence_content_parser.nodes.TasksReportMacro
   :show-inheritance:
   :members:
   :no-inherited-members:

ExcerptIncludeMacro
~~~~~~~~~~~~~~~~~~~

.. autoclass:: confluence_content_parser.nodes.ExcerptIncludeMacro
   :show-inheritance:
   :members:
   :no-inherited-members:

AttachmentsMacro
~~~~~~~~~~~~~~~~

.. autoclass:: confluence_content_parser.nodes.AttachmentsMacro
   :show-inheritance:
   :members:
   :no-inherited-members:

ViewPdfMacro
~~~~~~~~~~~~

.. autoclass:: confluence_content_parser.nodes.ViewPdfMacro
   :show-inheritance:
   :members:
   :no-inherited-members:

ViewFileMacro
~~~~~~~~~~~~~

.. autoclass:: confluence_content_parser.nodes.ViewFileMacro
   :show-inheritance:
   :members:
   :no-inherited-members:

ProfileMacro
~~~~~~~~~~~~

.. autoclass:: confluence_content_parser.nodes.ProfileMacro
   :show-inheritance:
   :members:
   :no-inherited-members:

AnchorMacro
~~~~~~~~~~~

.. autoclass:: confluence_content_parser.nodes.AnchorMacro
   :show-inheritance:
   :members:
   :no-inherited-members:

ExcerptMacro
~~~~~~~~~~~~

.. autoclass:: confluence_content_parser.nodes.ExcerptMacro
   :show-inheritance:
   :members:
   :no-inherited-members:

Decision and Task Nodes
-----------------------

DecisionListItemState
~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: confluence_content_parser.nodes.DecisionListItemState
   :show-inheritance:
   :no-members:

   Enumeration of decision list item states.

   **Values:**

   * ``DECIDED`` - Decision has been made
   * ``PENDING`` - Decision is pending

DecisionList
~~~~~~~~~~~~

.. autoclass:: confluence_content_parser.nodes.DecisionList
   :show-inheritance:
   :members:
   :no-inherited-members:

DecisionListItem
~~~~~~~~~~~~~~~~

.. autoclass:: confluence_content_parser.nodes.DecisionListItem
   :show-inheritance:
   :members:
   :no-inherited-members:

Utility Nodes
-------------

Fragment
~~~~~~~~

.. autoclass:: confluence_content_parser.nodes.Fragment
   :show-inheritance:
   :members:
   :no-inherited-members:

Emoticon
~~~~~~~~

.. autoclass:: confluence_content_parser.nodes.Emoticon
   :show-inheritance:
   :members:
   :no-inherited-members:

Time
~~~~

.. autoclass:: confluence_content_parser.nodes.Time
   :show-inheritance:
   :members:
   :no-inherited-members:

PlaceholderElement
~~~~~~~~~~~~~~~~~~

.. autoclass:: confluence_content_parser.nodes.PlaceholderElement
   :show-inheritance:
   :members:
   :no-inherited-members:

ResourceIdentifierType
~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: confluence_content_parser.nodes.ResourceIdentifierType
   :show-inheritance:
   :no-members:

   Enumeration of resource identifier types.

   **Values:**

   * ``PAGE`` - Page reference
   * ``BLOG_POST`` - Blog post reference
   * ``ATTACHMENT`` - Attachment reference
   * ``URL`` - URL reference
   * ``SHORTCUT`` - Shortcut reference
   * ``USER`` - User reference
   * ``SPACE`` - Space reference
   * ``CONTENT_ENTITY`` - Content entity reference

ResourceIdentifier
~~~~~~~~~~~~~~~~~~

.. autoclass:: confluence_content_parser.nodes.ResourceIdentifier
   :show-inheritance:
   :members:
   :no-inherited-members:

Usage Examples
--------------

For practical usage examples, see the :doc:`examples` section and the :doc:`user_guide`.