#!/usr/bin/env python3
"""Align the LAYOUT(...) tables in a QMK keymap.c to the keyboard's physical layout.

Every layer is rendered on the same column grid, derived from the key
coordinates in the keyboard's layout definition, so a given physical key sits
in the same screen column on every layer. Argument order is never changed --
only whitespace between tokens.

Usage: format_keymap.py <path/to/keymap.c> [--keyboard KB] [--check]
"""

import argparse
import json
import math
import os
import re
import subprocess
import sys


def names_from_path(path):
    """keyboards/<kb>/keymaps/<km>/keymap.c -> (<kb>, <km>)"""
    parts = os.path.abspath(path).split(os.sep)
    if "keyboards" not in parts or "keymaps" not in parts:
        return None, None
    kb_at, km_at = parts.index("keyboards"), parts.index("keymaps")
    keymap = parts[km_at + 1] if km_at + 1 < len(parts) - 1 else None
    return "/".join(parts[kb_at + 1 : km_at]), keymap


def load_layouts(keyboard, keymap=None):
    """Ask qmk for the fully-resolved layout data (handles revisions/defaults).

    Some keyboards only resolve when a keymap is named, so try that first.
    """
    attempts = []
    if keymap:
        attempts.append(["qmk", "info", "-kb", keyboard, "-km", keymap, "-f", "json"])
    attempts.append(["qmk", "info", "-kb", keyboard, "-f", "json"])

    last = None
    for cmd in attempts:
        run = subprocess.run(cmd, capture_output=True, text=True)
        if run.returncode == 0:
            info = json.loads(run.stdout)
            return info["layouts"], info.get("layout_aliases", {})
        last = run.stderr.strip() or run.stdout.strip()
    sys.exit(f"qmk info failed for {keyboard}: {last}")


def build_grid(layout):
    """Map each key index to (row, column slot).

    Columns come from rounding the physical x coordinate: keys that sit at the
    same place on the board land in the same slot even when their rows are
    staggered or offset (thumb clusters, inner encoder keys).

    Rows are contiguous runs of the argument list, broken wherever the column
    slot goes backwards. That keeps the emitted argument order identical to the
    input, which is what makes this safe to run on any keyboard.
    """
    keys = layout["layout"]
    # Round half *up*, not to even: banker's rounding would map 10.5 and 11.5
    # both toward 12 and destroy the left-to-right ordering of a row.
    slots = [math.floor(k["x"] + 0.5) for k in keys]

    rows, current = [], [0]
    for i in range(1, len(keys)):
        if slots[i] <= slots[i - 1]:
            rows.append(current)
            current = []
        current.append(i)
    rows.append(current)

    # A row must not put two keys in one slot; fall back to half-unit columns.
    if any(len(set(slots[i] for i in row)) != len(row) for row in rows):
        slots = [math.floor(k["x"] * 2 + 0.5) for k in keys]

    axis = sorted(set(slots))
    col_of = {s: n for n, s in enumerate(axis)}
    placement = {}
    for r, row in enumerate(rows):
        for i in row:
            placement[i] = (r, col_of[slots[i]])
    return placement, len(rows), len(axis)


TOKEN_SPLIT = re.compile(r"\s+")

# Comment text that is just table scaffolding, e.g. //|----+----|
SCAFFOLD = re.compile(r"^[\s\-+|,`'./\\_*]*$")


def mask_comments(src):
    """Blank out comments and string literals, keeping every byte offset intact.

    Scanning the masked copy means comment text can never be mistaken for a
    token or unbalance the parentheses, while the offsets it reports still
    point at the right places in the original source.
    """
    out = list(src)
    i, n = 0, len(src)
    while i < n:
        two = src[i : i + 2]
        if two == "//":
            j = src.find("\n", i)
            j = n if j < 0 else j
        elif two == "/*":
            j = src.find("*/", i + 2)
            j = n if j < 0 else j + 2
        elif src[i] in "\"'":
            quote, j = src[i], i + 1
            while j < n and src[j] != quote:
                j += 2 if src[j] == "\\" else 1
            j = min(j + 1, n)
        else:
            i += 1
            continue
        for k in range(i, j):
            if out[k] != "\n":
                out[k] = " "
        i = j
    return "".join(out)


def split_args(text):
    """Split a call's argument text on top-level commas."""
    args, depth, start = [], 0, 0
    for i, ch in enumerate(text):
        if ch in "([":
            depth += 1
        elif ch in ")]":
            depth -= 1
        elif ch == "," and depth == 0:
            args.append(text[start:i])
            start = i + 1
    args.append(text[start:])
    return [TOKEN_SPLIT.sub("", a) for a in args]


def find_calls(masked):
    """Yield (name, open_paren_index, close_paren_index, args) for LAYOUT calls.

    Takes the comment-masked source; offsets are valid in the original too.
    """
    for m in re.finditer(r"\bLAYOUT[A-Za-z0-9_]*\s*\(", masked):
        depth, i = 0, m.end() - 1
        while i < len(masked):
            if masked[i] == "(":
                depth += 1
            elif masked[i] == ")":
                depth -= 1
                if depth == 0:
                    break
            i += 1
        body = masked[m.end() : i]
        yield m.group(0).rstrip("( \t"), m.end(), i, split_args(body)


def dropped_comments(src, start, end):
    """Comments inside a LAYOUT body that are not just table scaffolding."""
    body = src[start:end]
    found = re.findall(r"//[^\n]*|/\*.*?\*/", body, re.S)
    return [c for c in found if not SCAFFOLD.match(c.lstrip("/*").rstrip("*/"))]


def render(args, placement, n_rows, n_cols, widths, indent="    "):
    cells = [[None] * n_cols for _ in range(n_rows)]
    for i, tok in enumerate(args):
        r, c = placement[i]
        cells[r][c] = tok

    lines = []
    for r, row in enumerate(cells):
        parts = []
        for c, tok in enumerate(row):
            w = widths[c]
            parts.append((tok + ",").ljust(w + 1) if tok is not None else " " * (w + 1))
        line = (indent + " ".join(parts)).rstrip().rstrip(",")
        if r < n_rows - 1:
            line += ","
        lines.append(line)
    return "\n" + "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("keymap")
    ap.add_argument("--keyboard", help="override keyboard name (default: infer from path)")
    ap.add_argument("--keymap-name", help="override keymap name used to resolve the layout")
    ap.add_argument("--check", action="store_true", help="exit 1 if reformatting would change the file")
    opts = ap.parse_args()

    inferred_kb, inferred_km = names_from_path(opts.keymap)
    keyboard = opts.keyboard or inferred_kb
    keymap_name = opts.keymap_name or inferred_km
    if not keyboard:
        sys.exit("could not infer keyboard name from path; pass --keyboard")

    layouts, aliases = load_layouts(keyboard, keymap_name)
    src = open(opts.keymap).read()
    masked = mask_comments(src)

    calls = list(find_calls(masked))
    if not calls:
        sys.exit("no LAYOUT(...) calls found")

    grids = {}
    for name, _, _, args in calls:
        target = aliases.get(name, name)
        if target not in layouts:
            sys.exit(f"{name} is not a layout of {keyboard}")
        if name not in grids:
            grids[name] = build_grid(layouts[target])
        placement, n_rows, n_cols = grids[name]
        if len(args) != len(placement):
            sys.exit(f"{name}: got {len(args)} keys, layout has {len(placement)}")

    # Column widths are shared by every layer using the same LAYOUT macro, so
    # the tables stack cleanly on top of each other.
    widths = {}
    for name, _, _, args in calls:
        placement, _, n_cols = grids[name]
        w = widths.setdefault(name, [0] * n_cols)
        for i, tok in enumerate(args):
            c = placement[i][1]
            w[c] = max(w[c], len(tok))

    out, last = [], 0
    for name, open_i, close_i, args in calls:
        placement, n_rows, n_cols = grids[name]
        for comment in dropped_comments(src, open_i, close_i):
            print(f"warning: dropping comment inside {name}: {comment.strip()[:70]}",
                  file=sys.stderr)
        out.append(src[last:open_i])
        out.append(render(args, placement, n_rows, n_cols, widths[name]))
        last = close_i
    out.append(src[last:])
    result = "".join(out)

    if opts.check:
        sys.exit(0 if result == src else 1)
    if result != src:
        open(opts.keymap, "w").write(result)
        print(f"formatted {opts.keymap}")
    else:
        print(f"{opts.keymap} already formatted")


if __name__ == "__main__":
    main()