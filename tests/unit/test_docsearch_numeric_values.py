from ansys_unified_mcp.analytics.docsearch.clean import clean_markdown


def test_clean_markdown_preserves_numeric_parameter_lines():
    source = "<!-- page 12 -->\nPort\n7450\nPort\n7460\nValue\n0\n"

    cleaned = clean_markdown(source)

    assert "<!-- page 12 -->" not in cleaned
    assert "Port\n7450\nPort\n7460\nValue\n0" in cleaned
