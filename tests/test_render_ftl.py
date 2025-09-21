from pathlib import Path

import pytest

from tools.render_ftl import PaperParseError, discover_documents, render_ftl


def write_paper(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_unique_fluent_keys_include_categories(tmp_path: Path) -> None:
    docs_dir = tmp_path / "docs"
    write_paper(docs_dir / "identity" / "id-replacement.paper", "[bold]Identity[/bold]\n")
    write_paper(docs_dir / "medical" / "id-replacement.paper", "[bold]Medical[/bold]\n")

    documents = discover_documents(docs_dir)
    keys = [doc.fluent_key for doc in documents]

    assert "doc-text-printer-identity-id-replacement" in keys
    assert "doc-text-printer-medical-id-replacement" in keys
    assert len(keys) == len(set(keys))


def test_skips_partial_directories(tmp_path: Path) -> None:
    docs_dir = tmp_path / "docs"
    write_paper(docs_dir / "security" / "incident.paper", "Details\n")
    write_paper(docs_dir / "_partials" / "footer.paper", "Footer\n")

    documents = discover_documents(docs_dir)
    assert len(documents) == 1
    assert documents[0].fluent_key == "doc-text-printer-security-incident"


def test_render_output_includes_category_headers(tmp_path: Path) -> None:
    docs_dir = tmp_path / "docs"
    write_paper(docs_dir / "Engineering" / "Power Plan.paper", "[bold]Plan[/bold]\n")

    documents = discover_documents(docs_dir)
    output = render_ftl(documents)

    assert "# Engineering" in output
    assert "doc-text-printer-engineering-power-plan" in output


def test_empty_document_raises(tmp_path: Path) -> None:
    docs_dir = tmp_path / "docs"
    empty_doc = docs_dir / "misc" / "blank.paper"
    empty_doc.parent.mkdir(parents=True, exist_ok=True)
    empty_doc.write_text("\n\n", encoding="utf-8")

    with pytest.raises(PaperParseError):
        discover_documents(docs_dir)