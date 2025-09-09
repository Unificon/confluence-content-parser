from confluence_content_parser import ConfluenceParser


def main() -> None:
    parser = ConfluenceParser()

    content = """
    <root>
      <ac:structured-macro ac:name="xyz"/>  
      <ac:link><ri:url ri:value="https://example.com"/></ac:link>
      <ac:link><ri:page ri:space-key="FOO" ri:content-title="Bar" ri:version-at-save="2"/></ac:link>
    </root>
    """

    doc = parser.parse(content)

    print("Top-level elements:")
    for el in doc.content:
        print(f"- type={el.type} kind={el.kind} id={el.id}")

    diags = doc.metadata.get("diagnostics") or []
    print("\nDiagnostics:")
    if not diags:
        print("(none)")
    else:
        for d in diags:
            print(f"- {d}")

    print("\nLinks and canonical URIs:")
    for el in doc.content:
        if el.type == "link" and el.link:
            print(f"- link kind={el.link.kind} canonical={el.link.canonical_uri}")


if __name__ == "__main__":
    main()
