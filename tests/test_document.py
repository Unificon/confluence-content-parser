#!/usr/bin/env python3

import pytest

from confluence_content_parser import (
    ConfluenceDocument,
    ConfluenceParser,
    Fragment,
    HeadingElement,
    PlaceholderElement,
)


class TestConfluenceDocument:
    """Test suite for ConfluenceDocument class."""

    def test_empty_document(self):
        """Test empty document behavior."""
        doc = ConfluenceDocument()
        assert doc.root is None
        assert doc.text == ""
        assert doc.find_all() == []
        assert doc.walk() == []

    def test_document_with_content(self):
        """Test document with actual content."""
        parser = ConfluenceParser()
        content = "<h1>Title</h1><p>Content</p>"
        doc = parser.parse(content)

        assert doc.root is not None
        assert "Title" in doc.text
        assert "Content" in doc.text

    def test_document_text_property(self):
        """Test document text property with line breaks."""
        parser = ConfluenceParser()
        content = "<h1>Title</h1><p>Paragraph 1</p><p>Paragraph 2</p>"
        doc = parser.parse(content)

        text = doc.text
        assert "Title" in text
        assert "Paragraph 1" in text
        assert "Paragraph 2" in text
        # Should have proper line breaks between block elements
        assert "\n\n" in text

    def test_find_all_by_type(self):
        """Test finding nodes by specific type."""
        parser = ConfluenceParser()
        content = "<h1>Title 1</h1><h2>Title 2</h2><p>Content</p>"
        doc = parser.parse(content)

        headings = doc.find_all(HeadingElement)
        assert len(headings) == 2

        all_nodes = doc.find_all()
        assert len(all_nodes) > 2

    def test_find_all_with_no_matches(self):
        """Test finding nodes when none match the type."""
        parser = ConfluenceParser()
        content = "<p>Simple paragraph</p>"
        doc = parser.parse(content)

        placeholders = doc.find_all(PlaceholderElement)
        assert len(placeholders) == 0

    def test_walk_document(self):
        """Test walking through all nodes in document."""
        parser = ConfluenceParser()
        content = "<p>Text with <strong>bold</strong> content</p>"
        doc = parser.parse(content)

        all_nodes = doc.walk()
        assert len(all_nodes) > 1
        # Should include both paragraph and text effect elements

    def test_document_metadata(self):
        """Test document metadata handling."""
        parser = ConfluenceParser(raise_on_finish=False)
        content = "<unknown-element>test</unknown-element>"
        doc = parser.parse(content)

        assert "diagnostics" in doc.metadata
        diagnostics = doc.metadata["diagnostics"]
        assert len(diagnostics) > 0

    def test_document_with_complex_structure(self):
        """Test document with complex nested structure."""
        parser = ConfluenceParser()
        content = """
        <ac:layout>
            <ac:layout-section ac:type="single">
                <ac:layout-cell>
                    <h1>Section Title</h1>
                    <p>Section content with <strong>formatting</strong></p>
                </ac:layout-cell>
            </ac:layout-section>
        </ac:layout>
        """
        doc = parser.parse(content)

        assert doc.root is not None
        assert "Section Title" in doc.text
        assert "Section content" in doc.text

    def test_document_consolidation_single_child(self):
        """Test document root consolidation with single child."""
        parser = ConfluenceParser()
        content = "<h1>Single Title</h1>"
        doc = parser.parse(content)

        # Should return the heading directly, not wrapped in Fragment
        assert isinstance(doc.root, HeadingElement)

    def test_document_consolidation_multiple_children(self):
        """Test document root consolidation with multiple children."""
        parser = ConfluenceParser()
        content = "<h1>Title</h1><p>Paragraph</p>"
        doc = parser.parse(content)

        # Should create Fragment to contain multiple children
        assert isinstance(doc.root, Fragment)
        assert len(doc.root.children) == 2


if __name__ == "__main__":
    pytest.main([__file__])
