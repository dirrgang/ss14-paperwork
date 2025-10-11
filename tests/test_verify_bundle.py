from pathlib import Path

import yaml

from tools.render_ftl import (
    discover_documents,
    render_documents_yaml,
    render_ftl,
    write_output,
)
from tools.render_starlight import (
    build_category_infos,
    render_lathe_categories,
    render_lathe_category_prototypes,
    render_recipe_pack,
    render_starlight_documents,
    render_starlight_recipes,
)
from tools.verify_bundle import verify_bundle


def write_paper(path: Path, title: str, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"# {title}\n{body}", encoding="utf-8")


def _generate_bundle(tmp_path: Path) -> dict[str, Path]:
    docs_dir = tmp_path / "docs"
    write_paper(docs_dir / "Identity" / "id-replacement.paper", "ID Replacement", "[body]\n")
    write_paper(docs_dir / "Security" / "incident.paper", "Incident Report", "[body]\n")

    documents = discover_documents(docs_dir)

    dist_dir = tmp_path / "dist"
    starlight_dir = dist_dir / "starlight"
    dist_dir.mkdir(parents=True, exist_ok=True)

    write_output(render_ftl(documents).rstrip("\n"), dist_dir / "doc-printer.ftl")
    write_output(render_documents_yaml(documents).rstrip("\n"), dist_dir / "documents.yml")

    categories = build_category_infos(documents, {})
    write_output(
        render_starlight_documents(documents, categories, hide_spawn_menu=True).rstrip("\n"),
        starlight_dir / "documents.yml",
    )
    write_output(
        render_starlight_recipes(
            documents,
            categories,
            recipe_categories={},
            completetime=2,
            materials={"SheetPrinter": 100},
            apply_discount=False,
        ).rstrip("\n"),
        starlight_dir / "printer.yml",
    )
    write_output(
        render_recipe_pack(documents, categories, pack_id="TestDocs").rstrip("\n"),
        starlight_dir / "pack_docs.yml",
    )
    write_output(
        render_lathe_categories(categories).rstrip("\n"),
        starlight_dir / "lathe-categories.ftl",
    )
    write_output(
        render_lathe_category_prototypes(categories).rstrip("\n"),
        starlight_dir / "categories.yml",
    )

    return {
        "documents_path": dist_dir / "documents.yml",
        "ftl_path": dist_dir / "doc-printer.ftl",
        "prototypes_path": starlight_dir / "documents.yml",
        "recipes_path": starlight_dir / "printer.yml",
        "pack_path": starlight_dir / "pack_docs.yml",
        "category_prototypes_path": starlight_dir / "categories.yml",
        "category_ftl_path": starlight_dir / "lathe-categories.ftl",
    }


def test_verify_bundle_accepts_valid_outputs(tmp_path: Path) -> None:
    paths = _generate_bundle(tmp_path)
    errors = verify_bundle(**paths)
    assert errors == []


def test_verify_bundle_detects_inconsistent_category(tmp_path: Path) -> None:
    paths = _generate_bundle(tmp_path)

    categories_path = paths["category_prototypes_path"]
    data = yaml.safe_load(categories_path.read_text(encoding="utf-8"))
    assert isinstance(data, list)
    data.pop()  # Remove last category definition
    categories_path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")

    errors = verify_bundle(**paths)
    assert errors
    assert any("lathe recipes reference undefined categories" in error for error in errors)
