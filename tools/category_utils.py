#!/usr/bin/env python3
"""Shared helpers for generating unique document category identifiers."""

from __future__ import annotations

from typing import Dict, Set


def alphabetic_suffix(index: int) -> str:
    """Return an alphabetical suffix sequence (A, B, ..., Z, AA, AB, ...)."""
    if index < 0:
        raise ValueError("index must be non-negative")
    result = ""
    value = index
    while True:
        value, remainder = divmod(value, 26)
        result = chr(ord("A") + remainder) + result
        if value == 0:
            break
        value -= 1
    return result


def ensure_document_slug(slug: str) -> str:
    """Ensure a slug is prefixed for document categories."""
    cleaned = slug.strip("-")
    if not cleaned:
        cleaned = "document"
    if not cleaned.startswith("document-"):
        cleaned = f"document-{cleaned}"
    return cleaned


def ensure_document_id(base: str) -> str:
    """Ensure an identifier contains the Document prefix."""
    cleaned = base or "Document"
    if not cleaned.lower().startswith("document"):
        cleaned = f"Document{cleaned}"
    return cleaned


def allocate_slug(base: str, existing: Set[str], counters: Dict[str, int]) -> str:
    """Allocate a unique slug, adding alphabetic suffixes if necessary."""
    key = base or "document"
    if key not in existing:
        existing.add(key)
        counters.setdefault(base, 0)
        return key

    counter = counters.get(base, 0)
    while True:
        suffix = alphabetic_suffix(counter).lower()
        candidate = f"{base}-{suffix}"
        counter += 1
        if candidate not in existing:
            existing.add(candidate)
            counters[base] = counter
            return candidate


def allocate_id(base: str, existing: Set[str], counters: Dict[str, int]) -> str:
    """Allocate a unique identifier, appending alphabetic suffixes when needed."""
    identifier = base or "Document"
    if identifier not in existing:
        existing.add(identifier)
        counters.setdefault(base, 0)
        return identifier

    counter = counters.get(base, 0)
    while True:
        suffix = alphabetic_suffix(counter)
        candidate = f"{base}{suffix}"
        counter += 1
        if candidate not in existing:
            existing.add(candidate)
            counters[base] = counter
            return candidate
