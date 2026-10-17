---
name: format_km
description: Align the LAYOUT(...) tables in a QMK keymap.c so each key sits in the screen column matching its physical position on the board, with columns shared across all layers. Use when a keymap is hard to read, when layers have drifted out of alignment after edits, or when asked to "format the keymap" / "line up the keymap".
---

# Format a QMK keymap

Rewrites the whitespace inside every `LAYOUT(...)` call in a `keymap.c` so the
tables read like the physical keyboard. Token order is never changed — only the
spacing between tokens — so the compiled firmware is identical.

## Run it

```bash
python3 .claude/skills/format_km/format_keymap.py keyboards/<kb>/keymaps/<km>/keymap.c
```

The keyboard and keymap names are inferred from the path. Override with
`--keyboard` / `--keymap-name` when the file lives elsewhere. `--check` exits 1
if the file would change and writes nothing (useful in a pre-commit hook).

Requires the `qmk` CLI on PATH; it is used to resolve the keyboard's layout
data, including revisions and `layout_aliases`.

## Then verify

Always compile afterwards — it is the only real proof that the key count and
argument order survived:

```bash
qmk compile -kb <kb> -km <km>
```

## How the grid is derived

- **Columns**: each key's physical `x` from the layout definition, rounded half
  up. Keys that sit at the same place on the board share a column even across
  different rows, so offset thumb clusters and inner encoder keys line up under
  the main grid. If that would put two keys of one row in the same column, it
  retries at half-unit resolution.
- **Rows**: contiguous runs of the argument list, broken wherever the column
  goes backwards. This is what guarantees the emitted order matches the input.
- **Widths**: shared by every layer using the same `LAYOUT` macro, so the layer
  tables stack exactly on top of each other.

## Things to watch for

- **Comments inside a `LAYOUT(...)` body are removed.** They are almost always
  ASCII table scaffolding (`//|-----+-----|`) that the alignment replaces. Any
  comment that is *not* pure scaffolding is reported on stderr before it is
  dropped — read those warnings and re-add anything that mattered. Comments
  outside the `LAYOUT(...)` calls, including the layout diagram above the
  keymaps array, are untouched.
- **Very long keycodes widen a whole column** on every layer. If one
  `MT(MOD_x, KC_y)` blows out the table, define a short alias for it near the
  top of the file and use that instead.
- Prefer the short keycode aliases (`KC_RGHT`, `KC_MINS`, `KC_BSLS`) over the
  long spellings to keep columns narrow.

## Complementary manual step

The script only touches the tables. If the file's layout diagram comment is
missing or stale, write one above the `keymaps` array showing the physical
board with the same column positions the tables use — label the main grid, the
encoder/inner keys, and the thumb cluster. Read the coordinates from
`qmk info -kb <kb> -f json` rather than guessing.
