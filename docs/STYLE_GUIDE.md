# Paperwork Style Guide

## Core Principles

- Begin every document with `# Title` so tooling can surface the display name.
- Lead with prompts that can be satisfied by ticking a box; only ask for free-form writing when no structured option fits.
- Assume the document will be filled out in-game; keep prompts short and end them with a colon.
- Use placeholders so crew interact with fields without editing the document (`[form]` for typed input, `[signature]` for an autofill of the character's full name and position, `[check]` for checkboxes).
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
- Drop in `[signature]` wherever the full name and position of the character writing the document is required.
- Signatures and stamps make the document read-only. That means, a document must not require any further input after a signature or stamp is applied.
- You can also use `[signature]` to speed up adding the character's name in printed forms. However, forms should ideally be written in such a way, that the name should only be filled out once, at the top.

Example:

```
Name and Position: [signature]

Department Access Needed:
[check] Command        [check] Science
[check] Engineering    [check] Medical [check]
[check] Security       [check] Other: [form]

Reason for request:
[form]

[italic]Place for stamps[/italic]
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
ff2fff Clown
9fed58 Food Service (Bartender/Chef/Botany/Service)
6e6e6e Passenger
1b67a5 Command
009100 CentComm
134975 NanoTrasen
ff0000 Syndicate
```

## Document Types

| **Prefix**    | **Type**      | **Purpose**                                   | **Direction**   | **Examples**                                                         |
| ------------- | ------------- | --------------------------------------------- | --------------- | -------------------------------------------------------------------- |
| `Report_`     | Report        | Record facts, events, conditions              | Informational   | Incident Report, Arrest Report, SITREP, Morgue Report                |
| `Request_`    | Request       | Ask for approval, resources, or authorization | Upward-facing   | ID Replacement Request, Access Change Request, ERT Request           |
| `Order_`      | Order         | Issue binding directive                       | Downward-facing | Execution Order, Access Revocation Order, Parole Order               |
| `Permission_` | Permission    | Grant rights/privileges normally restricted   | Downward-facing | Weapon Carry Permission, Search Permission, Body Disposal Permission |
| `Statement_`  | Statement     | Declare personal status or intent             | Declarative     | Employment Statement, Resignation Statement, Interim Appointment     |
| `Complaint_`  | Complaint     | File grievances or allege wrongdoing          | Upward-facing   | Labor Violation Complaint, Offense Complaint                         |
| `Form_`       | Form          | General-purpose, neutral paperwork            | Neutral         | Medical Consent Form, Visitor Registration Form, Lost & Found Form   |
| `Comm_`       | Communication | Official correspondence or memos              | Flexible        | CentComm Communication, Internal Memo                                |
| `Notice_`     | Notice        | Provide warnings or acknowledgments           | Outward-facing  | Trespass Notice, Removal Notice                                      |
| `Misc_`       | Miscellaneous | Anything not covered by the above             | Variable        | Special event paperwork, experimental docs                           |

### Naming Convention

- **Filenames** must follow the pattern:

  ```
  <Type>_<Descriptor>
  ```

  Example: `Report_Incident_General.txt`, `Request_ID_Replacement.txt`

- **Header** must include both **authority** and **type**:

  ```
  [head=2][color=#003366][bold]STATION COMMAND DOCUMENT – REQUEST[/bold][/color][/head]
  [center][color=#0055aa][bolditalic]ID CARD REPLACEMENT REQUEST[/bolditalic][/color][/center]
  ```

- **Descriptors** should be concise, CamelCase or underscores. Avoid vague names like `Form1` or `Request_Something`.

### Practical Tip

- **If the document is informational** → `Report`.
- **If it asks for approval** → `Request`.
- **If it commands action** → `Order`.
- **If it grants rights** → `Permission`.
- **If it’s a personal declaration** → `Statement`.
- **If it alleges wrongdoing** → `Complaint`.
- **If it’s neutral paperwork** → `Form`.
- **If it’s correspondence** → `Comm`.
- **If it’s a warning** → `Notice`.
- **If nothing fits** → `Misc`.

## Pre-submission Checks

- Confirm every fillable field now uses `[form]`, `[signature]`, or `[check]` as appropriate; there should be no leftover placeholder text for players to delete manually.
- Ensure each prompt either presents interactive checkboxes or a `[form]` so players are never typing on blank space; add visual guides only when necessary.
- Run `python tools/check_docs.py` before committing to catch duplicate paperwork or missing stamp sections.
- Proofread for length limits on `[head]` tags and trim wording until they meet the character caps.
