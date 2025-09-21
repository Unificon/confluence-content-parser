Installation
============

Requirements
------------

* Python 3.12 or higher
* lxml >=6.0.1
* pydantic >=2.11.7
* types-lxml >=2025.8.25

Installing from PyPI
--------------------

.. code-block:: bash

   # Using uv (recommended)
   uv add confluence-content-parser

   # Using pip
   pip install confluence-content-parser

Installing from Source
----------------------

.. code-block:: bash

   git clone https://github.com/Unificon/confluence-content-parser.git
   cd confluence-content-parser
   uv sync

Development Installation
-----------------------

For development, install with development dependencies:

.. code-block:: bash

   git clone https://github.com/Unificon/confluence-content-parser.git
   cd confluence-content-parser
   uv sync --dev

Verifying Installation
---------------------

To verify the installation works correctly:

.. code-block:: python

   from confluence_content_parser import ConfluenceParser

   parser = ConfluenceParser()
   print("Confluence Content Parser installed successfully!")

Dependencies
-----------

The library uses modern, well-maintained dependencies:

* **lxml**: For fast and robust XML parsing
* **pydantic**: For data validation and serialization with type safety
* **types-lxml**: For enhanced type hints when using lxml

Development Dependencies
-----------------------

For development and testing:

* **black**: Code formatting
* **ruff**: Fast Python linter
* **mypy**: Static type checking
* **pytest**: Testing framework
* **pytest-cov**: Test coverage reporting