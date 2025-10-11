from pathlib import Path

import pytest

from tools.render_ftl import (
    FTL_PREFIX_MARKER,
    PaperParseError,
    discover_documents,
    render_documents_yaml,
    render_ftl,
)


def write_paper(path: Path, title: str, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    content = f"# {title}\n{body}"
    path.write_text(content, encoding="utf-8")


def test_unique_fluent_keys_include_categories(tmp_path: Path) -> None:
    docs_dir = tmp_path / "docs"
    write_paper(
        docs_dir / "identity" / "id-replacement.paper",
        "ID Replacement",
        "[bold]Identity[/bold]\n",
    )
    write_paper(
        docs_dir / "medical" / "id-replacement.paper",
        "ID Replacement",
        "[bold]Medical[/bold]\n",
    )

    documents = discover_documents(docs_dir)
    keys = [doc.fluent_key for doc in documents]

    assert "doc-text-printer-identity-id-replacement" in keys
    assert "doc-text-printer-medical-id-replacement" in keys
    assert len(keys) == len(set(keys))


def test_skips_partial_directories(tmp_path: Path) -> None:
    docs_dir = tmp_path / "docs"
    write_paper(docs_dir / "security" / "incident.paper", "Incident", "Details\n")
    write_paper(docs_dir / "_partials" / "footer.paper", "Footer", "Footer body\n")

    documents = discover_documents(docs_dir)
    assert len(documents) == 1
    assert documents[0].fluent_key == "doc-text-printer-security-incident"


def test_render_output_includes_category_headers(tmp_path: Path) -> None:
    docs_dir = tmp_path / "docs"
    write_paper(
        docs_dir
        / "04 Engineering & Logistics (Engineering, Cargo, Janitorial)"
        / "Power Plan.paper",
        "Power Plan",
        "[bold]Plan[/bold]\n",
    )

    documents = discover_documents(docs_dir)
    output = render_ftl(documents)

    assert "# Engineering & Logistics" in output
    assert "doc-text-printer-engineering-logistics-power-plan" in output


def test_documents_yaml_contains_titles(tmp_path: Path) -> None:
    docs_dir = tmp_path / "docs"
    write_paper(
        docs_dir / "identity" / "id-replacement.paper",
        "ID Replacement Request",
        "[bold]Identity[/bold]\n",
    )

    documents = discover_documents(docs_dir)
    yaml_output = render_documents_yaml(documents)

    assert 'documents:' in yaml_output
    assert 'key: "doc-text-printer-identity-id-replacement"' in yaml_output
    assert 'name: "ID Replacement Request"' in yaml_output
    assert '      - "Identity"' in yaml_output


def test_missing_title_line_raises(tmp_path: Path) -> None:
    docs_dir = tmp_path / "docs"
    doc_path = docs_dir / "misc" / "blank.paper"
    doc_path.parent.mkdir(parents=True, exist_ok=True)
    doc_path.write_text("No title\n", encoding="utf-8")

    with pytest.raises(PaperParseError):
        discover_documents(docs_dir)


def test_empty_document_raises(tmp_path: Path) -> None:
    docs_dir = tmp_path / "docs"
    doc_path = docs_dir / "misc" / "blank.paper"
    doc_path.parent.mkdir(parents=True, exist_ok=True)
    doc_path.write_text("\n\n", encoding="utf-8")

    with pytest.raises(PaperParseError):
        discover_documents(docs_dir)


def test_render_ftl_bracket_lines_prefixed(tmp_path: Path) -> None:
    docs_dir = tmp_path / "docs"
    write_paper(
        docs_dir / "identity" / "logo-test.paper",
        "Logo Test",
        "[logo]\nSome text\n",
    )

    documents = discover_documents(docs_dir)
    output = render_ftl(documents)

    lines = output.splitlines()
    key_index = lines.index("doc-text-printer-identity-logo-test =")
    assert lines[key_index + 1] == f"    {FTL_PREFIX_MARKER}[logo]"
    assert lines[key_index + 2] == "    Some text"
    assert lines[key_index + 3] == f"    {FTL_PREFIX_MARKER}"
    assert lines[key_index + 4] == f"    {FTL_PREFIX_MARKER}"
