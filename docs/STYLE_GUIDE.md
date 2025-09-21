# Paperwork Style Guide

## Writing Guidelines

- Assume the document will be filled out in-game; keep prompts short and end them with a colon.
- Leave blank lines where crew members need to write detailed responses.
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
> `[bullet/]` - insert a bullet point (great for lists)
>
> `[bold][/bold]`, `[italic][/italic]` - add emphasis

Combine bold and italic tags, or use the shortcut `[bolditalic][/bolditalic]`.

Remember to wrap text between the opening and closing tags. For example, typing `[bold]Hello![/bold]` produces **Hello!** on paper.

Color tags support hexadecimal values or most HTML color names:

- `[color=#ff0000]` ... `[/color]` renders as red.
- `[color=red]` ... `[/color]` accomplishes the same thing.

Commonly used colors sourced from job icons:

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
009100 CentComm
134975 NanoTrasen
ff0000 Syndicate
```

## Additional Resources

- Copy starter layouts from `docs/_templates/` when creating new forms.
- Run `python tools/check_docs.py` to flag duplicate paperwork or missing stamp sections before submitting a PR.
