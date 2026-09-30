#!/usr/bin/env python3
"""Remove the auto-generated language pie from the 3D contribution graph SVG.

yoshi389111/github-profile-3d-contrib always draws a language pie into its
`normal` output, at a fixed position derived from the canvas constants:

    x = 40
    y = height - pieHeight - 70 = 850 - 260 - 70 = 520

so the pie group is always `<g transform="translate(40, 520)">`. There is no
setting to turn it off, and the pie is driven by commit counts grouped by each
repository's primary language -- which misrepresents this profile (one large
C++ learning repo dominates, while upstream PRs are still open and therefore
barely counted). We strip it and use a hand-authored chart instead.

The group is removed by balanced-tag scanning, so nesting stays valid.
Fails loudly if the marker is missing or ambiguous, so a change in the
upstream action is noticed instead of silently shipping a wrong chart.
"""

from __future__ import annotations

import pathlib
import sys

TARGET = pathlib.Path("profile-3d-contrib/profile-3d.svg")
PIE_MARKER = '<g transform="translate(40, '


def strip_group(svg: str, marker: str) -> str:
    start = svg.find(marker)
    depth = 0
    i = start
    while True:
        next_open = svg.find("<g", i)
        next_close = svg.find("</g>", i)
        if next_close == -1:
            raise ValueError("unbalanced <g> while scanning the pie group")
        if next_open != -1 and next_open < next_close:
            depth += 1
            i = next_open + 2
        else:
            depth -= 1
            i = next_close + 4
            if depth == 0:
                return svg[:start] + svg[i:]


def main() -> int:
    if not TARGET.is_file():
        print(f"[strip-lang-pie] missing {TARGET}", file=sys.stderr)
        return 1

    svg = TARGET.read_text(encoding="utf-8")

    count = svg.count(PIE_MARKER)
    if count != 1:
        print(
            f"[strip-lang-pie] expected exactly 1 pie group, found {count}",
            file=sys.stderr,
        )
        return 1

    before = len(svg)
    svg = strip_group(svg, PIE_MARKER)

    if PIE_MARKER in svg:
        print("[strip-lang-pie] pie marker still present after strip", file=sys.stderr)
        return 1
    if svg.count("<g") != svg.count("</g>"):
        print("[strip-lang-pie] <g> tags unbalanced after strip", file=sys.stderr)
        return 1

    TARGET.write_text(svg, encoding="utf-8")
    print(f"[strip-lang-pie] removed {before - len(svg)} bytes ({before} -> {len(svg)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
