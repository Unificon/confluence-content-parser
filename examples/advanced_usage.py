#!/usr/bin/env python3
"""Advanced usage examples for confluence-content-parser."""

from confluence_content_parser import ConfluenceParser


def main():
    content = '''
    <ac:layout>
      <ac:layout-section ac:type="fixed-width">
        <ac:layout-cell>
          <h2>Title</h2>
          <p>Para with <ac:link><ri:url ri:value="https://example.com"/></ac:link></p>
          <ac:image ac:alt="Screenshot"><ri:attachment ri:filename="shot.png"/></ac:image>
          <table>
            <tbody>
              <tr><th>Header 1</th><th>Header 2</th></tr>
              <tr><td>A</td><td>B</td></tr>
            </tbody>
          </table>
          <ac:structured-macro ac:name="excerpt">
            <ac:rich-text-body><p>Excerpt body</p></ac:rich-text-body>
          </ac:structured-macro>
        </ac:layout-cell>
      </ac:layout-section>
    </ac:layout>
    '''

    parser = ConfluenceParser()
    doc = parser.parse(content)

    print("Top-level elements:", len(doc.content))
    root = doc.content[0]

    print("Root id:", root.id)

    # Gather content from layout cells
    layout_contents = []
    for child in root.children:
        if child.type == "layout_section" and child.layout_section:
            for cell in child.layout_section.cells:
                layout_contents.extend(cell.content)

    # Compute kinds across layout subtree
    subtree = []
    for el in layout_contents:
        subtree.extend(list(el.iter()))
    print("Kinds in subtree:", {el.kind for el in subtree})
    print("Root path:", root.path)

    # Links
    links = [el for el in subtree if el.type == "link" and el.link]
    print("Links URIs:", [lnk.link.canonical_uri for lnk in links])
    print("Links kinds:", [lnk.link.kind for lnk in links])

    # Tables
    tables = [el for el in subtree if el.type == "table" and el.table]
    if tables:
        t = tables[0].table
        header_texts = [" ".join((c.text or c.text_normalized()) for c in cell).strip() for cell in t.cells[0]]
        print("Table headers:", header_texts)
        body_texts = [" ".join((c.text or c.text_normalized()) for c in cell).strip() for cell in t.cells[1]]
        print("First row:", body_texts)

    # Excerpt macro
    excerpts = [el for el in subtree if el.type == "excerpt_macro" and el.excerpt_macro]
    if excerpts:
        ex = excerpts[0].excerpt_macro
        body_text = " ".join(e.text_normalized() for e in ex.children)
        print("Excerpt children text:", body_text)

    # Paragraph example
    paras = [el for el in subtree if el.type == "p"]
    if paras:
        p = paras[0]
        print("Paragraph id:", p.id)
        print("Paragraph path:", p.path)
        print("Paragraph list scope:", p.list_scope)
        print("Paragraph layout scope:", p.layout_scope)

    print("Diagnostics:", doc.metadata.get("diagnostics"))


if __name__ == "__main__":
    main()


