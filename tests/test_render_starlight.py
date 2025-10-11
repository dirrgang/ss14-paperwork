from pathlib import Path

from tools.render_ftl import discover_documents
from tools.render_starlight import (
    build_category_infos,
    render_lathe_categories,
    render_lathe_category_prototypes,
    render_recipe_pack,
    render_starlight_documents,
    render_starlight_recipes,
)


def write_paper(path: Path, title: str, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"# {title}\n{body}", encoding="utf-8")


def test_render_outputs_cover_all_sections(tmp_path: Path) -> None:
    docs_dir = tmp_path / "docs"
    write_paper(
        docs_dir / "01 Identity" / "id-replacement.paper",
        "ID Replacement",
        "[form]\n",
    )
    write_paper(
        docs_dir / "02 Security" / "access-review.paper",
        "Access Review",
        "[form]\n",
    )

    documents = discover_documents(docs_dir)
    categories = build_category_infos(documents, {})

    prototypes = render_starlight_documents(documents, categories, hide_spawn_menu=True)
    assert "PrintedDocumentIdentityIdReplacement" in prototypes
    assert "categories: [ HideSpawnMenu ]" in prototypes

    recipes = render_starlight_recipes(
        documents,
        categories,
        recipe_categories={},
        completetime=3,
        materials={"SheetPrinter": 40},
        apply_discount=False,
    )
    assert "PrintedDocumentIdentityIdReplacementRecipe" in recipes
    assert "# Security" in recipes
    assert "    - Identity" in recipes
    assert "    - Security" in recipes
    assert "SheetPrinter: 40" in recipes

    pack = render_recipe_pack(documents, categories, pack_id="MyDocs")
    assert "- type: latheRecipePack" in pack
    assert "MyDocs" in pack
    assert "PrintedDocumentSecurityAccessReviewRecipe" in pack

    lathe_categories = render_lathe_categories(categories)
    assert "lathe-category-identity" in lathe_categories
    assert "lathe-category-security" in lathe_categories
    lathe_category_prototypes = render_lathe_category_prototypes(categories)
    assert "- type: latheCategory" in lathe_category_prototypes
    assert "id: Identity" in lathe_category_prototypes
    assert "name: lathe-category-security" in lathe_category_prototypes


def test_duplicate_category_slugs_get_disambiguated(tmp_path: Path) -> None:
    docs_dir = tmp_path / "docs"
    write_paper(
        docs_dir / "Alpha" / "first.paper",
        "First",
        "[body]\n",
    )
    write_paper(
        docs_dir / "Alpha!!" / "second.paper",
        "Second",
        "[body]\n",
    )

    documents = discover_documents(docs_dir)
    categories = build_category_infos(documents, {})

    lathe_categories = render_lathe_categories(categories)
    assert "lathe-category-alpha = Alpha" in lathe_categories
    assert "lathe-category-alpha-a = Alpha!!" in lathe_categories
    prototype_output = render_lathe_category_prototypes(categories)
    assert "id: Alpha" in prototype_output
    assert "id: AlphaA" in prototype_output
