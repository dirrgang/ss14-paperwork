# Contributing

## Authoring rules

- Each form is a plain-text `.paper` file; do not add YAML front matter.
- Start every document with a leading `# Human Readable Title` so metadata exports can display it.
- Place documents under `docs/<category>/...`; nested folders become additional categories and are reflected in the Fluent key (e.g., `identity/id-replacement` -> `doc-text-printer-identity-id-replacement`).
- Review `docs/STYLE_GUIDE.md` before writing to stay consistent with formatting, reusable headers/footers, and lore expectations.
- Keep fields concise and end prompts with a colon where helpful.
- Avoid placeholder text that must be deleted by players; provide blanks instead.
- Stamp areas are required whenever a document expects stamping in-game.

## Tooling

- Run `python tools/render_ftl.py` after editing paperwork to refresh `dist/doc-printer.ftl` and `dist/documents.yml`.
- Run `python tools/check_docs.py` to flag duplicate bodies or missing stamp sections (`--fail-on-duplicates` and `--strict-stamps` are available).
- Execute `pytest` to keep the generator tests green.
- CI executes the render script on every push to validate the bundle is up to date.

## PR checklist

- Commit the regenerated `dist/doc-printer.ftl` and `dist/documents.yml` alongside documentation changes.
- Ensure the forms render correctly in the Starlight document printer.
- Reference templates in `docs/_templates/` (headers, footers, page parts) wherever they fit to keep layouts consistent.
