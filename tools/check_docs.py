#!/usr/bin/env python3
"""Run sanity checks against paperwork documents."""

from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from pathlib import Path
from typing import Iterable, List

from render_ftl import PaperParseError, discover_documents


def normalise_body(lines: Iterable[str]) -> str:
    """Squash insignificant whitespace so duplicate forms are easier to spot."""
    stripped = [line.strip() for line in lines if line.strip()]
    return "\n".join(stripped)


def check_documents(docs_dir: Path, strict_stamps: bool, fail_on_duplicates: bool) -> int:
    try:
        documents = discover_documents(docs_dir)
    except PaperParseError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    duplicate_map: dict[str, List[str]] = defaultdict(list)
    missing_stamp: List[str] = []

    for doc in documents:
        body_key = normalise_body(doc.body_lines)
        if body_key:
            duplicate_map[body_key].append(str(doc.path.relative_to(docs_dir)))

        has_stamp = any("stamp" in line.lower() for line in doc.body_lines)
        if not has_stamp:
            missing_stamp.append(str(doc.path.relative_to(docs_dir)))

    warnings: List[str] = []
    errors: List[str] = []

    for docs in duplicate_map.values():
        if len(docs) > 1:
            message = "duplicate body content across: " + ", ".join(sorted(docs))
            if fail_on_duplicates:
                errors.append(message)
            else:
                warnings.append(message)

    if missing_stamp:
        message = "missing possible stamp area: " + ", ".join(sorted(missing_stamp))
        if strict_stamps:
            errors.append(message)
        else:
            warnings.append(message)

    for warning in warnings:
        print(f"warning: {warning}")

    for error in errors:
        print(f"error: {error}", file=sys.stderr)

    return 1 if errors else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--docs-dir",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "docs",
        help="Directory containing paperwork (.paper files)",
    )
    parser.add_argument(
        "--strict-stamps",
        action="store_true",
        help="Fail when paperwork lacks a stamp section.",
    )
    parser.add_argument(
        "--fail-on-duplicates",
        action="store_true",
        help="Treat duplicate body content as an error instead of a warning.",
    )
    return parser


def main(argv: List[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    return check_documents(args.docs_dir, args.strict_stamps, args.fail_on_duplicates)


if __name__ == "__main__":
    raise SystemExit(main())