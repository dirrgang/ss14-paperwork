# SS14 Paperwork (Text Source)

Plain-text `.paper` forms converted into a Starlight-compatible document printer bundle.

- Text: CC-BY 4.0
- Tools: MIT
- Outputs: `dist/doc-printer.ftl`, `dist/documents.yml` (MIT)

## How to use

- Add or edit forms under `docs/**`. Sub-folders define the document categories; the filename is the slug.
- Begin every document with `# Human Readable Title` so the generator can surface display names.
- Run `python tools/render_ftl.py` to regenerate both the Fluent bundle and `documents.yml` after changing paperwork.
- Run `python tools/render_starlight.py` to emit Starlight-ready prototypes, recipes, and lathe pack fragments under `dist/starlight/`.
- Run `python tools/verify_bundle.py` to confirm every generated asset references valid paperwork entries and categories.
- Run `python tools/check_docs.py` to spot duplicate bodies or missing stamp sections.
- Fluent keys follow `doc-text-printer-{category-path}-{slug}` to keep entries unique across categories.
- On push, CI runs the same script so downstream consumers stay in sync.

### Starlight exports

`tools/render_starlight.py` reuses the paperwork parser and writes five artefacts to `dist/starlight/`:

- `documents.yml` for `PrintedDocumentâ€¦` prototypes (hidden from the spawn menu by default).
- `printer.yml` for document-printer lathe recipes, using `SheetPrinter=100` unless overridden.
- `pack_docs.yml` to bulk-register the generated recipes into a lathe recipe pack.
- `lathe-categories.ftl` with Fluent entries for any category labels used in the outputs.
- `categories.yml` with `latheCategory` prototype definitions referencing those Fluent keys.

Categories in `dist/documents.yml` use the same PascalCase identifiers that appear in `categories.yml` to keep downstream wiring consistent.
Use python tools/verify_bundle.py after rendering to check for broken links between these artefacts.

Pass `--category-config` with a JSON object keyed by the top-level paperwork directory name to override labels, ordering, or Fluent keys. Example:

```json
{
  "01 Identity & Employment": {
    "lathe_label": "Identity paperwork",
    "lathe_key": "identity",
    "comment": "Identity & Employment",
    "order": 10
  }
}
```

Further fine-tuning is available through `--lathe-category`, `--material`, `--lathe-category-prototypes-output`, and `--show-in-spawn-menu`; run the script with `--help` for details.

## Authoring resources

- Follow the guidance in `docs/STYLE_GUIDE.md` for formatting, tone, color tags, and reusable parts.
- Copy starter layouts from `docs/_templates/`:
  - Whole-form examples such as `neutral.paper`, `departmental.paper`, `centcomm.paper`, or `station-command.paper`.
  - Subfolders like `page_parts/` for mix-and-match building blocks (graphs, checklists, etc.).

## Testing

```bash
python -m venv .venv
. .venv/Scripts/Activate.ps1
pip install -r requirements.txt
python tools/render_ftl.py --docs-dir docs --output dist/doc-printer.ftl --documents-output dist/documents.yml
python tools/check_docs.py
pytest
```