#!/usr/bin/env python3
"""Validate that generated paperwork outputs stay internally consistent."""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Dict, Iterable, List, Set, Tuple

import yaml


FTL_ENTRY_RE = re.compile(r"^(?P<key>[a-z0-9\-]+)\s*=")


def _read_yaml_sequence(path: Path) -> List[dict]:
    text = path.read_text(encoding="utf-8")
    data = yaml.safe_load(text)
    if data is None:
        return []
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        # Some files store a single top-level mapping (e.g. documents.yaml).
        return [data]
    raise TypeError(f"Unsupported YAML structure in {path}: expected list or dict.")


def _parse_ftl_keys(path: Path, expected_prefix: str) -> Set[str]:
    keys: Set[str] = set()
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        match = FTL_ENTRY_RE.match(stripped)
        if not match:
            continue
        key = match.group("key")
        if key.startswith(expected_prefix):
            keys.add(key)
    return keys


def _extract_documents(documents_path: Path) -> Tuple[Dict[str, dict], Set[str]]:
    data = yaml.safe_load(documents_path.read_text(encoding="utf-8")) or {}
    documents = data.get("documents") or []
    doc_map: Dict[str, dict] = {}
    categories: Set[str] = set()
    for entry in documents:
        key = entry.get("key")
        if not key:
            continue
        doc_map[key] = entry
        for cat in entry.get("categories") or []:
            categories.add(cat)
    return doc_map, categories


def verify_bundle(
    documents_path: Path,
    ftl_path: Path,
    prototypes_path: Path,
    recipes_path: Path,
    pack_path: Path,
    category_prototypes_path: Path,
    category_ftl_path: Path,
) -> List[str]:
    """Return a list of consistency issues discovered across generated outputs."""
    errors: List[str] = []

    doc_map, doc_category_ids = _extract_documents(documents_path)
    if not doc_map:
        errors.append(f"No documents found in {documents_path}")

    doc_keys = set(doc_map.keys())

    ftl_keys = _parse_ftl_keys(ftl_path, "doc-text-printer-")
    missing_ftl = doc_keys - ftl_keys
    if missing_ftl:
        joined = ", ".join(sorted(missing_ftl))
        errors.append(f"doc-printer.ftl missing entries for: {joined}")

    prototypes = _read_yaml_sequence(prototypes_path)
    entity_ids: Dict[str, dict] = {}
    for entry in prototypes:
        if entry.get("type") != "entity":
            continue
        entity_id = entry.get("id")
        if not entity_id:
            errors.append(f"Entity entry missing id in {prototypes_path}")
            continue
        if entity_id in entity_ids:
            errors.append(f"Duplicate entity id {entity_id} in {prototypes_path}")
            continue
        entity_ids[entity_id] = entry
        components = entry.get("components") or []
        paper = next((comp for comp in components if comp.get("type") == "Paper"), None)
        if not paper:
            errors.append(f"{entity_id} missing Paper component in {prototypes_path}")
            continue
        content_key = paper.get("content")
        if content_key not in doc_keys:
            errors.append(
                f"{entity_id} references unknown paperwork key '{content_key}'"
            )

    recipes = _read_yaml_sequence(recipes_path)
    recipe_ids: Dict[str, dict] = {}
    recipe_category_ids: Set[str] = set()
    for entry in recipes:
        if entry.get("type") != "latheRecipe":
            continue
        recipe_id = entry.get("id")
        if not recipe_id:
            errors.append(f"Recipe entry missing id in {recipes_path}")
            continue
        if recipe_id in recipe_ids:
            errors.append(f"Duplicate recipe id {recipe_id} in {recipes_path}")
            continue
        recipe_ids[recipe_id] = entry

        result = entry.get("result")
        if result not in entity_ids:
            errors.append(f"{recipe_id} references unknown entity '{result}'")

        for cat in entry.get("categories") or []:
            recipe_category_ids.add(cat)

    pack_entries = _read_yaml_sequence(pack_path)
    for entry in pack_entries:
        if entry.get("type") != "latheRecipePack":
            continue
        for recipe_id in entry.get("recipes") or []:
            if recipe_id not in recipe_ids:
                errors.append(
                    f"Recipe pack {entry.get('id')} references unknown recipe '{recipe_id}'"
                )

    category_prototypes = _read_yaml_sequence(category_prototypes_path)
    lathe_category_ids: Dict[str, str] = {}
    for entry in category_prototypes:
        if entry.get("type") != "latheCategory":
            continue
        category_id = entry.get("id")
        if not category_id:
            errors.append(f"latheCategory entry missing id in {category_prototypes_path}")
            continue
        if category_id in lathe_category_ids:
            errors.append(f"Duplicate latheCategory id {category_id}")
            continue
        name = entry.get("name")
        if not isinstance(name, str) or not name:
            errors.append(f"latheCategory {category_id} missing name in prototypes")
            continue
        lathe_category_ids[category_id] = name

    missing_category_ids = doc_category_ids - set(lathe_category_ids.keys())
    if missing_category_ids:
        joined = ", ".join(sorted(missing_category_ids))
        errors.append(f"documents.yml references undefined lathe categories: {joined}")

    missing_recipe_categories = recipe_category_ids - set(lathe_category_ids.keys())
    if missing_recipe_categories:
        joined = ", ".join(sorted(missing_recipe_categories))
        errors.append(f"lathe recipes reference undefined categories: {joined}")

    category_ftl_keys = _parse_ftl_keys(category_ftl_path, "lathe-category-")
    missing_ftl_categories = set(lathe_category_ids.values()) - category_ftl_keys
    if missing_ftl_categories:
        joined = ", ".join(sorted(missing_ftl_categories))
        errors.append(
            f"lathe-categories.ftl missing definitions for: {joined}"
        )

    undefined_ftl_categories = category_ftl_keys - set(lathe_category_ids.values())
    if undefined_ftl_categories:
        joined = ", ".join(sorted(undefined_ftl_categories))
        errors.append(
            f"lathe-categories.ftl defines unused categories: {joined}"
        )

    unused_category_ids = set(lathe_category_ids.keys()) - doc_category_ids
    for cat in unused_category_ids:
        if cat not in recipe_category_ids:
            errors.append(f"latheCategory '{cat}' is not referenced by documents or recipes")

    missing_recipe_category_usage = set(lathe_category_ids.keys()) - recipe_category_ids
    if missing_recipe_category_usage:
        joined = ", ".join(sorted(missing_recipe_category_usage))
        errors.append(f"No recipes reference categories: {joined}")

    return errors


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--documents",
        type=Path,
        default=Path("dist/documents.yml"),
        help="Path to generated documents.yml.",
    )
    parser.add_argument(
        "--doc-printer",
        type=Path,
        default=Path("dist/doc-printer.ftl"),
        help="Path to generated doc-printer.ftl.",
    )
    parser.add_argument(
        "--starlight-documents",
        type=Path,
        default=Path("dist/starlight/documents.yml"),
        help="Path to generated Starlight PrintedDocument prototypes.",
    )
    parser.add_argument(
        "--starlight-recipes",
        type=Path,
        default=Path("dist/starlight/printer.yml"),
        help="Path to generated Starlight lathe recipes.",
    )
    parser.add_argument(
        "--starlight-pack",
        type=Path,
        default=Path("dist/starlight/pack_docs.yml"),
        help="Path to generated Starlight recipe pack.",
    )
    parser.add_argument(
        "--starlight-categories",
        type=Path,
        default=Path("dist/starlight/categories.yml"),
        help="Path to generated latheCategory prototypes.",
    )
    parser.add_argument(
        "--lathe-categories-ftl",
        type=Path,
        default=Path("dist/starlight/lathe-categories.ftl"),
        help="Path to generated lathe categories Fluent file.",
    )
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    errors = verify_bundle(
        args.documents,
        args.doc_printer,
        args.starlight_documents,
        args.starlight_recipes,
        args.starlight_pack,
        args.starlight_categories,
        args.lathe_categories_ftl,
    )

    if errors:
        for error in errors:
            print(f"error: {error}")
        return 1

    print("Bundle outputs verified: all references resolved.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
