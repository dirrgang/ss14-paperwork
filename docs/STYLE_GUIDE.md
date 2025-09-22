---
Foo:
---
# Paperwork Style Guide

## Core Principles

- Begin every document with `# Title` so tooling can surface the display name.
- Lead with prompts that can be satisfied by ticking a box; only ask for free-form writing when no structured option fits.
- Assume the document will be filled out in-game; keep prompts short and end them with a colon.
- Use placeholders so crew interact with fields without editing the document (`[form]` for typed input, `[signature]` for automatic signatures, `[check]` for checkboxes).
- Reserve decorative elements for official paperwork (department logos, separators) and keep general-use forms minimal.
- Include an explicit stamp area (`[italic]Place for stamps[/italic]`) whenever the document needs to be validated.
- Prefer clear, modern language; avoid lore that contradicts the upstream SS14 setting.

## Formatting and Syntax

Using an in-game pen, you can write on paper or in books. Pens are stored in your PDA alongside Space Law and your ID.

The following formatting is available:

> `[color=color][/color]` - change the color of enclosed text
>
> `[head=n][/head]` - use heading level `n` (1 to 4)
>
> `[bullet]` - insert a bullet point (great for lists)
>
> `[bold][/bold]`, `[italic][/italic]` - add emphasis

Combine bold and italic tags, or use the shortcut `[bolditalic][/bolditalic]`.

Remember to wrap text between the opening and closing tags. For example, typing `[bold]Hello![/bold]` produces **Hello!** on paper.

Color tags support hexadecimal values or most HTML color names:

- `[color=#ff0000]` ... `[/color]` renders as red.
- `[color=red]` ... `[/color]` accomplishes the same thing.

### Placeholders

This repository assumes the fork can recognize interactive placeholders that replace manual blue-ink prompts:

- `[form]` prompts the user for text input and inserts their response.
- `[signature]` resolves to the current crew member's signature automatically.
- `[check]` renders an in-paper checkbox that can be toggled.

Placeholders can sit on the same line as a prompt or on the following line when you want to give the player more room. They may be combined with emphasis or color tags when needed.

## Prompt Patterns

- Offer the common answers first and attach `[check]` placeholders so they can be toggled directly; reserve an `Other:` line with its own `[form]` when edge cases appear.
- Pair each checkbox choice with a short label that can fit on one line.
- When lists are long, split them into logical clusters separated by a blank line or a `[bullet]` label.
- Keep any free-response request to a single prompt and place it after the structured options; include a `[form]` so it opens the text entry window.

## Player Input Styling

- Use `[form]` on the same line as short responses (Name, Position) and place it on a new line when you expect a paragraph.
- Append `[check]` at the end of each checkbox label so it toggles cleanly; align them in columns with spaces when you want a wider layout.
- Drop in `[signature]` wherever a signature is required. For multi-party signatures, repeat the prompt plus `[signature]` on separate lines. You can also use `[signature]` to speed up adding the character's name in printed forms. However, forms should ideally be written in such a way, that the name should only be filled out once, at the top.

Example:

```
Name: [form]
Department:
[check] Engineering    [check] Medical [check]
[check] Security       [check] Other: [form]

Reason for request:
[form]

Signature: [signature]
```

## Headings

- Use `[head=1]` for the document title and keep the text <= 27 characters.
- Use `[head=2]` for major sections and keep the text <= 37 characters.
- `[head=3]` and `[head=4]` are acceptable for sub-sections, but prefer concise phrases that fit on one line.
- Avoid nested heading levels inside tables or choice blocks; use plain labels instead.

## Color Reference

```
cb0000 Security
c96dbf Science
5b97bc Medical
b18644 Cargo
f39f27 Engineering
ff2fff Clown (how special)
9fed58 Food Service (Bartender/Chef/Botany/Service)
6e6e6e Passenger
1b67a5 Command
002aaf Player Input (Blue Ink)
009100 CentComm
134975 NanoTrasen
ff0000 Syndicate
```

## Pre-submission Checks

- Confirm every fillable field now uses `[form]`, `[signature]`, or `[check]` as appropriate; there should be no leftover placeholder text for players to delete manually.
- Ensure each prompt either presents interactive checkboxes or a `[form]` so players are never typing on blank space; add visual guides only when necessary.
- Run `python tools/check_docs.py` before committing to catch duplicate paperwork or missing stamp sections.
- Proofread for length limits on `[head]` tags and trim wording until they meet the character caps.
