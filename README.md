# SS14 Paperwork (Text Source)

Plain-text `.paper` forms converted into a Starlight-compatible document printer bundle.

- Text: CC-BY 4.0
- Tools: MIT
- Outputs: `dist/doc-printer.ftl`, `dist/documents.yml` (MIT)

## How to use

- Add or edit forms under `docs/**`. Sub-folders define the document categories; the filename is the slug.
- Begin every document with `# Human Readable Title` so the generator can surface display names.
- Run `python tools/render_ftl.py` to regenerate both the Fluent bundle and `documents.yml` after changing paperwork.
- Run `python tools/check_docs.py` to spot duplicate bodies or missing stamp sections.
- Fluent keys follow `doc-text-printer-{category-path}-{slug}` to keep entries unique across categories.
- On push, CI runs the same script so downstream consumers stay in sync.

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
