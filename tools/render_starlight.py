#!/usr/bin/env python3
"""Generate Starlight prototype and recipe data from paperwork documents."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
import sys
from typing import Dict, List, Mapping, MutableMapping, Sequence

if __package__:
    from .category_utils import allocate_id, allocate_slug, ensure_document_id, ensure_document_slug
    from .render_ftl import (
        PaperDocument,
        PaperParseError,
        discover_documents,
        normalise_component,
        to_pascal_case,
        write_output,
    )
else:
    CURRENT_DIR = Path(__file__).resolve().parent
    PARENT_DIR = CURRENT_DIR.parent
    if str(CURRENT_DIR) not in sys.path:
        sys.path.insert(0, str(CURRENT_DIR))
    if str(PARENT_DIR) not in sys.path:
        sys.path.insert(0, str(PARENT_DIR))
    from category_utils import allocate_id, allocate_slug, ensure_document_id, ensure_document_slug
    from render_ftl import (
        PaperDocument,
        PaperParseError,
        discover_documents,
        normalise_component,
        to_pascal_case,
        write_output,
    )

ST_DEFAULT_MATERIALS = {"SheetPrinter": 100}


@dataclass(slots=True)
class CategoryInfo:
    """Describe how a paperwork category maps onto Starlight assets."""

    raw_label: str
    lathe_label: str
    lathe_key: str
    lathe_id: str
    comment: str
    order: int


def primary_category(doc: PaperDocument) -> str:
    """Return the primary (top-level) category label for a paperwork document."""
    if doc.categories:
        return doc.categories[0]
    return "Miscellaneous"


def load_category_overrides(path: Path | None) -> Dict[str, Dict[str, object]]:
    """Read optional JSON category overrides keyed by the primary category label."""
    if path is None:
        return {}
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in {path}: {exc}") from exc

    if not isinstance(raw, dict):
        raise ValueError(f"Category overrides must be a JSON object at {path}")

    clean: Dict[str, Dict[str, object]] = {}
    for key, value in raw.items():
        if not isinstance(value, dict):
            raise ValueError(f"Override for '{key}' must be an object, got {type(value).__name__}")
        clean[key] = value
    return clean


def build_category_infos(
    documents: Sequence[PaperDocument],
    overrides: Mapping[str, Dict[str, object]],
) -> List[CategoryInfo]:
    """Construct ordered category metadata derived from discovered documents."""
    infos: Dict[str, CategoryInfo] = {}
    existing_keys: set[str] = set()
    key_counters: Dict[str, int] = {}
    existing_ids: set[str] = set()
    id_counters: Dict[str, int] = {}
    order_counter = 0

    for doc in documents:
        category = primary_category(doc)
        if category in infos:
            continue

        override = overrides.get(category, {})
        lathe_label = str(override.get("lathe_label", category))

        lathe_key_override = override.get("lathe_key")
        if isinstance(lathe_key_override, str) and lathe_key_override.strip():
            override_slug = normalise_component(lathe_key_override)
        else:
            override_slug = ""
        base_slug = (
            override_slug
            or normalise_component(lathe_label)
            or normalise_component(category)
            or "misc"
        )
        base_slug = ensure_document_slug(base_slug)
        lathe_key = allocate_slug(base_slug, existing_keys, key_counters)

        lathe_id_override = override.get("lathe_id")
        if isinstance(lathe_id_override, str) and lathe_id_override.strip():
            base_id_source = lathe_id_override.strip()
        else:
            base_id_source = to_pascal_case(lathe_label) or to_pascal_case(category)

        if not base_id_source:
            base_id_source = to_pascal_case(category) or "Category"
        base_id = ensure_document_id(base_id_source)
        lathe_id = allocate_id(base_id, existing_ids, id_counters)

        comment = str(override.get("comment", lathe_label))
        order_value = override.get("order")
        if isinstance(order_value, int):
            order = order_value
        else:
            order = order_counter
        order_counter += 1

        infos[category] = CategoryInfo(
            raw_label=category,
            lathe_label=lathe_label,
            lathe_key=lathe_key,
            lathe_id=lathe_id,
            comment=comment,
            order=order,
        )

    ordered_infos = sorted(
        infos.values(),
        key=lambda info: (info.order, info.lathe_label.lower(), info.raw_label.lower()),
    )
    return ordered_infos


def entity_id_for(doc: PaperDocument) -> str:
    """Derive the Starlight entity id for a paperwork document."""
    key = doc.fluent_key
    prefix = "doc-text-printer-"
    if key.startswith(prefix):
        key = key[len(prefix) :]
    components = [part for part in key.split("-") if part]
    filtered = [part for part in components if not part.isdigit()]
    filtered_key = "-".join(filtered) if filtered else key
    suffix = to_pascal_case(filtered_key)
    return f"PrintedDocument{suffix}"


def recipe_id_for(entity_id: str) -> str:
    """Generate the lathe recipe id for a given entity id."""
    return f"{entity_id}Recipe"


def render_starlight_documents(
    documents: Sequence[PaperDocument],
    categories: Sequence[CategoryInfo],
    hide_spawn_menu: bool,
) -> str:
    """Render the entity prototypes for the provided paperwork documents."""
    by_category: MutableMapping[str, List[PaperDocument]] = {}
    for doc in documents:
        category = primary_category(doc)
        by_category.setdefault(category, []).append(doc)

    header = "# Auto-generated by tools/render_starlight.py. Do not edit manually."
    lines: List[str] = [header]

    for info in categories:
        docs = by_category.get(info.raw_label)
        if not docs:
            continue
        docs_sorted = sorted(docs, key=lambda doc: doc.title.casefold())

        lines.append("")
        lines.append(f"# {info.comment}")
        lines.append("")

        for doc in docs_sorted:
            entity_id = entity_id_for(doc)
            lines.append("- type: entity")
            lines.append("  parent: PrintedDocument")
            lines.append(f"  id: {entity_id}")
            lines.append(f"  name: {doc.title}")
            if hide_spawn_menu:
                lines.append("  categories: [ HideSpawnMenu ]")
            lines.append("  components:")
            lines.append("    - type: Paper")
            lines.append(f"      content: {doc.fluent_key}")
            lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def render_starlight_recipes(
    documents: Sequence[PaperDocument],
    categories: Sequence[CategoryInfo],
    recipe_categories: Mapping[str, str],
    completetime: int,
    materials: Mapping[str, int],
    apply_discount: bool,
) -> str:
    """Render lathe recipe prototypes for paperwork documents."""
    by_category: MutableMapping[str, List[PaperDocument]] = {}
    for doc in documents:
        category = primary_category(doc)
        by_category.setdefault(category, []).append(doc)

    header = "# Auto-generated by tools/render_starlight.py. Do not edit manually."
    lines: List[str] = [header]

    for info in categories:
        docs = by_category.get(info.raw_label)
        if not docs:
            continue
        docs_sorted = sorted(docs, key=lambda doc: doc.title.casefold())
        lines.append("")
        lines.append(f"# {info.comment}")
        lines.append("")

        lathe_category_id = recipe_categories.get(info.raw_label, info.lathe_id)

        for doc in docs_sorted:
            entity_id = entity_id_for(doc)
            recipe_id = recipe_id_for(entity_id)
            lines.append("- type: latheRecipe")
            lines.append(f"  id: {recipe_id}")
            lines.append(f"  result: {entity_id}")
            lines.append("  categories:")
            lines.append(f"    - {lathe_category_id}")
            lines.append(f"  completetime: {completetime}")
            lines.append(f"  applyMaterialDiscount: {str(apply_discount).lower()}")
            lines.append("  materials:")
            for material, amount in materials.items():
                lines.append(f"    {material}: {amount}")
            lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def render_recipe_pack(
    documents: Sequence[PaperDocument],
    categories: Sequence[CategoryInfo],
    pack_id: str,
) -> str:
    """Render the lathe recipe pack block wiring paperwork recipes together."""
    by_category: MutableMapping[str, List[PaperDocument]] = {}
    for doc in documents:
        category = primary_category(doc)
        by_category.setdefault(category, []).append(doc)

    header = "# Auto-generated by tools/render_starlight.py. Do not edit manually."
    lines: List[str] = [header]
    lines.append(f"- type: latheRecipePack")
    lines.append(f"  id: {pack_id}")
    lines.append("  recipes:")

    for info in categories:
        docs = by_category.get(info.raw_label)
        if not docs:
            continue
        docs_sorted = sorted(docs, key=lambda doc: doc.title.casefold())
        lines.append(f"  # {info.comment}")
        for doc in docs_sorted:
            entity_id = entity_id_for(doc)
            recipe_id = recipe_id_for(entity_id)
            lines.append(f"  - {recipe_id}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def render_lathe_categories(categories: Sequence[CategoryInfo]) -> str:
    """Render Fluent lathe category entries."""
    header = "# Auto-generated by tools/render_starlight.py. Do not edit manually."
    lines: List[str] = [header]

    for info in categories:
        lines.append(f"lathe-category-{info.lathe_key} = {info.lathe_label}")

    lines.append("")
    return "\n".join(lines)


def render_lathe_category_prototypes(categories: Sequence[CategoryInfo]) -> str:
    """Render latheCategory prototype entries."""
    header = "# Auto-generated by tools/render_starlight.py. Do not edit manually."
    lines: List[str] = [header]

    for info in categories:
        lines.append("")
        lines.append("- type: latheCategory")
        lines.append(f"  id: {info.lathe_id}")
        lines.append(f"  name: lathe-category-{info.lathe_key}")

    lines.append("")
    return "\n".join(lines)


def parse_recipe_categories(mapping_args: Sequence[str]) -> Dict[str, str]:
    """Parse optional category id overrides."""
    mapping: Dict[str, str] = {}
    for arg in mapping_args:
        if "=" not in arg:
            raise ValueError(f"Invalid category override '{arg}'. Use '<category>=<id>'.")
        category, label = arg.split("=", 1)
        category = category.strip()
        label = label.strip()
        if not category or not label:
            raise ValueError(f"Invalid category override '{arg}'. Empty components are not allowed.")
        mapping[category] = label
    return mapping


def parse_materials(material_args: Sequence[str]) -> Dict[str, int]:
    """Parse lathe material requirements passed as NAME=AMOUNT pairs."""
    if not material_args:
        return dict(ST_DEFAULT_MATERIALS)

    materials: Dict[str, int] = {}
    for arg in material_args:
        if "=" not in arg:
            raise ValueError(f"Invalid material specification '{arg}'. Use '<name>=<amount>'.")
        name, value_text = arg.split("=", 1)
        name = name.strip()
        value_text = value_text.strip()
        if not name or not value_text:
            raise ValueError(f"Invalid material specification '{arg}'. Empty components are not allowed.")
        try:
            value = int(value_text)
        except ValueError as exc:
            raise ValueError(f"Material amount for '{name}' must be an integer, got '{value_text}'.") from exc
        materials[name] = value
    return materials


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--docs-dir",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "docs",
        help="Directory containing paperwork source documents.",
    )
    parser.add_argument(
        "--prototypes-output",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "dist" / "starlight" / "documents.yml",
        help="Destination path for generated PrintedDocument prototypes.",
    )
    parser.add_argument(
        "--recipes-output",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "dist" / "starlight" / "printer.yml",
        help="Destination path for generated printer lathe recipes.",
    )
    parser.add_argument(
        "--pack-output",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "dist" / "starlight" / "pack_docs.yml",
        help="Destination path for generated lathe recipe pack entries.",
    )
    parser.add_argument(
        "--lathe-categories-output",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "dist" / "starlight" / "lathe-categories.ftl",
        help="Destination path for generated lathe category Fluent entries.",
    )
    parser.add_argument(
        "--lathe-category-prototypes-output",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "dist" / "starlight" / "categories.yml",
        help="Destination path for generated lathe category prototypes.",
    )
    parser.add_argument(
        "--category-config",
        type=Path,
        help="Optional JSON file mapping primary paperwork categories to output metadata.",
    )
    parser.add_argument(
        "--lathe-category",
        action="append",
        default=[],
        metavar="CATEGORY=ID",
        help=(
            "Override the lathe category id referenced by generated recipes for a paperwork "
            "category. Use the cleaned paperwork category name on the left."
        ),
    )
    parser.add_argument(
        "--material",
        action="append",
        metavar="NAME=AMOUNT",
        help="Add or override a lathe material requirement (defaults to SheetPrinter=100).",
    )
    parser.add_argument(
        "--recipe-time",
        type=int,
        default=2,
        help="Completion time for generated lathe recipes (default: 2).",
    )
    parser.add_argument(
        "--pack-id",
        default="StarlightDocsAuto",
        help="Identifier for the generated lathe recipe pack.",
    )
    parser.add_argument(
        "--show-in-spawn-menu",
        action="store_true",
        help="Do not add the HideSpawnMenu category to generated prototypes.",
    )
    parser.add_argument(
        "--apply-material-discount",
        action="store_true",
        help="Toggle applyMaterialDiscount for generated recipes (default false).",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    try:
        documents = discover_documents(args.docs_dir)
    except PaperParseError as exc:
        parser.error(str(exc))
        return 2

    try:
        overrides = load_category_overrides(args.category_config)
        recipe_category_overrides = parse_recipe_categories(args.lathe_category)
        materials = parse_materials(args.material or [])
    except ValueError as exc:
        parser.error(str(exc))
        return 2

    categories = build_category_infos(documents, overrides)
    prototypes_text = render_starlight_documents(documents, categories, not args.show_in_spawn_menu)
    recipes_text = render_starlight_recipes(
        documents,
        categories,
        recipe_category_overrides,
        args.recipe_time,
        materials,
        args.apply_material_discount,
    )
    pack_text = render_recipe_pack(documents, categories, args.pack_id)
    lathe_categories_text = render_lathe_categories(categories)
    lathe_category_prototypes_text = render_lathe_category_prototypes(categories)

    changes: List[str] = []
    if write_output(prototypes_text.rstrip("\n"), args.prototypes_output):
        changes.append(str(args.prototypes_output))
    if write_output(recipes_text.rstrip("\n"), args.recipes_output):
        changes.append(str(args.recipes_output))
    if write_output(pack_text.rstrip("\n"), args.pack_output):
        changes.append(str(args.pack_output))
    if write_output(lathe_categories_text.rstrip("\n"), args.lathe_categories_output):
        changes.append(str(args.lathe_categories_output))
    if write_output(lathe_category_prototypes_text.rstrip("\n"), args.lathe_category_prototypes_output):
        changes.append(str(args.lathe_category_prototypes_output))

    if changes:
        joined = ", ".join(changes)
        print(f"Updated {joined} for {len(documents)} document(s).")
    else:
        print("Starlight exports already up to date.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
