#!/usr/bin/env python3
"""Generate doc-printer.ftl and companion metadata from .paper documents."""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Tuple

FTL_PREFIX_MARKER = "\u200b"  # zero-width space to avoid Fluent select parsing


class PaperParseError(RuntimeError):
    """Raised when a .paper document cannot be processed."""


def strip_parenthetical(text: str) -> str:
    """Remove parenthetical segments and collapse surrounding whitespace."""
    without_parentheses = re.sub(r"\s*\([^()]*\)", "", text)
    collapsed = re.sub(r"\s+", " ", without_parentheses)
    return collapsed.strip()


def normalise_component(component: str) -> str:
    """Produce a filesystem/path-safe slug component."""
    cleaned = strip_parenthetical(component)
    cleaned = cleaned.lower().replace(" ", "-")
    cleaned = re.sub(r"[^a-z0-9-]+", "-", cleaned)
    cleaned = re.sub(r"\d+", "", cleaned)
    cleaned = re.sub(r"-+", "-", cleaned).strip("-")
    return cleaned


def clean_category_label(component: str) -> str:
    """Return a human-readable category label without parenthetical notes."""
    cleaned = strip_parenthetical(component).strip()
    without_prefix = re.sub(r"^\d+\s*[-.)]?\s*", "", cleaned)
    result = without_prefix.strip()
    return result or cleaned


def to_pascal_case(value: str) -> str:
    """Convert a string into PascalCase segments."""
    parts = re.split(r"[^0-9a-zA-Z]+", value)
    result_parts: List[str] = []
    for part in parts:
        if not part:
            continue
        if part.isdigit():
            continue
        stripped = re.sub(r"\d+", "", part)
        if not stripped:
            continue
        result_parts.append(stripped[0].upper() + stripped[1:].lower())
    return "".join(result_parts)


def yaml_quote(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace("\"", "\\\"")
    return f'"{escaped}"'


@dataclass(slots=True)
class PaperDocument:
    path: Path
    categories: Tuple[str, ...]
    category_keys: Tuple[str, ...]
    slug: str
    slug_key: str
    title: str
    body_lines: List[str]

    @property
    def category_label(self) -> str:
        if not self.categories:
            return "uncategorized"
        return " / ".join(self.categories)

    @property
    def fluent_key(self) -> str:
        parts = [*self.category_keys, self.slug_key]
        filtered = [part for part in parts if part]
        suffix = "-".join(filtered) if filtered else "paper"
        return f"doc-text-printer-{suffix}"


def list_document_paths(root: Path) -> List[Path]:
    candidates: set[Path] = set()
    for pattern in ("*.txt", "*.paper"):
        for path in root.rglob(pattern):
            candidates.add(path)

    paths: List[Path] = []
    for path in sorted(candidates):
        if should_skip(path, root):
            continue
        paths.append(path)
    return paths


def should_skip(path: Path, root: Path) -> bool:
    try:
        relative_parts = path.relative_to(root).parts
    except ValueError:
        return True
    return any(part.startswith("_") for part in relative_parts)


def discover_documents(root: Path) -> List[PaperDocument]:
    documents: List[PaperDocument] = []
    for path in list_document_paths(root):
        documents.append(parse_document(path, root))
    if not documents:
        raise PaperParseError(f"No .paper documents found under {root}")
    return documents


def parse_document(path: Path, root: Path) -> PaperDocument:
    try:
        raw_text = path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise PaperParseError(f"Missing document: {path}") from exc

    if not raw_text.strip():
        raise PaperParseError(f"Document {path} is empty")

    normalised = raw_text.replace("\r\n", "\n").replace("\r", "\n")
    lines = normalised.split("\n")

    if not lines or not lines[0].lstrip().startswith("#"):
        raise PaperParseError(
            f"Document {path} must begin with a title line (e.g. '# Title')."
        )

    title_line = lines[0].lstrip()[1:].strip()
    if not title_line:
        raise PaperParseError(f"Title line in {path} is empty")

    body_lines = lines[1:]

    raw_categories = path.relative_to(root).parent.parts
    display_categories = tuple(
        filter(None, (clean_category_label(part) for part in raw_categories))
    )
    category_keys = tuple(
        filter(None, (normalise_component(part) for part in display_categories))
    )

    slug = path.stem
    slug_key = normalise_component(slug)
    if not slug_key:
        fallback = re.sub(r"\d+", "", slug.lower())
        slug_key = fallback or "document"

    return PaperDocument(
        path=path,
        categories=display_categories,
        category_keys=category_keys,
        slug=slug,
        slug_key=slug_key,
        title=title_line,
        body_lines=body_lines,
    )


def render_ftl(documents: Iterable[PaperDocument]) -> str:
    docs = sorted(documents, key=lambda doc: (doc.categories, doc.slug))

    lines: List[str] = []
    lines.append("# Auto-generated by tools/render_ftl.py. Do not edit manually.")
    lines.append("# Source docs: docs/*.txt")

    current_category: Tuple[str, ...] | None = None
    for doc in docs:
        if doc.categories != current_category:
            lines.append("")
            lines.append(f"# {doc.category_label}")
            current_category = doc.categories

        lines.append("")
        lines.append(f"# title: {doc.title}")
        lines.append(f"# slug: {doc.slug}")
        lines.append(f"{doc.fluent_key} =")
        body_lines = list(doc.body_lines)
        while body_lines and not body_lines[-1].strip():
            body_lines.pop()
        if body_lines:
            for raw_line in body_lines:
                formatted_line = raw_line
                if formatted_line.startswith("["):
                    # Fluent treats lines beginning with '[' as select variants. Prefix a zero-width
                    # space so the document renders while preserving legacy markup.
                    formatted_line = FTL_PREFIX_MARKER + formatted_line
                lines.append(f"    {formatted_line}")
        # Always add trailing blank lines so in-game rendering gets vertical spacing.
        lines.append(f"    {FTL_PREFIX_MARKER}")
        lines.append(f"    {FTL_PREFIX_MARKER}")
    lines.append("")
    return "\n".join(lines)


def render_documents_yaml(documents: Iterable[PaperDocument]) -> str:
    docs = sorted(documents, key=lambda doc: (doc.categories, doc.slug))

    lines: List[str] = []
    lines.append("# Auto-generated by tools/render_ftl.py. Do not edit manually.")
    lines.append("documents:")
    for doc in docs:
        lines.append("  - key: " + yaml_quote(doc.fluent_key))
        lines.append("    name: " + yaml_quote(doc.title))
        if doc.categories:
            primary_category = doc.categories[0]
            primary_key = normalise_component(primary_category)
            primary_id = to_pascal_case(primary_key) if primary_key else to_pascal_case(primary_category)
            category_value = primary_id or primary_category
            lines.append("    categories:")
            lines.append("      - " + yaml_quote(category_value))
    lines.append("")
    return "\n".join(lines)


def write_output(content: str, destination: Path) -> bool:
    destination.parent.mkdir(parents=True, exist_ok=True)
    new_text = content + "\n"
    if destination.exists():
        current_text = destination.read_text(encoding="utf-8")
        if current_text == new_text:
            return False
    destination.write_text(new_text, encoding="utf-8")
    return True


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--docs-dir",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "docs",
        help="Path to the directory containing .paper documents",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "dist" / "doc-printer.ftl",
        help="Destination path for the generated Fluent file",
    )
    parser.add_argument(
        "--documents-output",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "dist" / "documents.yml",
        help="Destination path for the generated documents metadata",
    )
    return parser


def main(argv: List[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    try:
        documents = discover_documents(args.docs_dir)
        ftl_output = render_ftl(documents)
        yaml_output = render_documents_yaml(documents)
        ftl_changed = write_output(ftl_output, args.output)
        yaml_changed = write_output(yaml_output, args.documents_output)

        if ftl_changed and yaml_changed:
            status = "Updated both"
        elif ftl_changed:
            status = "Updated"
        elif yaml_changed:
            status = "Updated"
        else:
            status = "Up to date"
        targets = ", ".join(
            str(path)
            for changed, path in (
                (ftl_changed, args.output),
                (yaml_changed, args.documents_output),
            )
            if changed
        )
        if not targets:
            targets = f"{args.output}, {args.documents_output}"
        print(f"{status} {targets} from {len(documents)} document(s).")
        return 0
    except PaperParseError as exc:
        parser.error(str(exc))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
