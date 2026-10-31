"""Curses-free screen model (SPEC-06 sections 2 and 7).

The acceptance tests only need `render_frame`, which starts a new game with the
scenario's premade party, closes the opening paragraph pop-up and renders the
first frame into an 80 x 25 text buffer.
"""

from __future__ import annotations

import os

from . import headless

GLYPHS = '.:"=,so~^bTYH*O%#_;/+nhPp|w`XGK>'

STATUS_ROW = 0
VIEWPORT_TOP = 1
VIEWPORT_LEFT = 0
VIEWPORT_W = 39
VIEWPORT_H = 11
PARTY_LEFT = 40
PARTY_TOP = 1
HELP_TOP = 9
LOG_TOP = 12
LOG_H = 11
PROMPT_ROW = 23
KEY_ROW = 24

WIDTH = 80
HEIGHT = 25


def glyph_for_image(image):
    """SPEC-06 section 2.3: image t + 10 shows the glyph of tile t."""
    if image is None:
        return "?"
    if 0 <= image <= 9:
        return str(image)
    t = image - 10
    if 0 <= t < len(GLYPHS):
        return GLYPHS[t]
    return "?"


def _blank():
    return [" " * WIDTH for _ in range(HEIGHT)]


def _put(buf, row, col, text):
    if not (0 <= row < HEIGHT):
        return
    line = buf[row]
    if col < 0:
        text = text[-col:]
        col = 0
    if col >= WIDTH:
        return
    text = text[: WIDTH - col]
    buf[row] = line[:col] + text + line[col + len(text):]


def render_status_line(state):
    """SPEC-06 section 2.1: location name, Day N, HH:MM, (x,y), Steps N, mode."""
    parts = [
        str(state.get("location_name", "")),
        "Day %d" % state.get("day", 1),
        "%02d:%02d" % (state.get("hour", 0), state.get("minute", 0)),
        "(%d,%d)" % (state.get("x", 0), state.get("y", 0)),
        "Steps %d" % state.get("steps", 0),
        str(state.get("mode", "map")),
    ]
    return "  ".join(parts)


def render_viewport(state):
    """SPEC-06 section 2.2: 39 x 11 cells, party at viewport cell (19, 5)."""
    tiles = state.get("tiles") or []
    border_image = state.get("border_image", 0)
    border = glyph_for_image(border_image)
    px, py = state.get("x", 0), state.get("y", 0)
    rows = []
    for j in range(VIEWPORT_H):
        row = []
        for i in range(VIEWPORT_W):
            if (i, j) == (19, 5):
                row.append("@")
                continue
            x = px - 19 + i
            y = py - 5 + j
            if 0 <= y < len(tiles) and 0 <= x < len(tiles[y]):
                row.append(glyph_for_image(tiles[y][x]))
            else:
                row.append(border)
        rows.append("".join(row))
    return rows


def render_party_panel(state):
    """SPEC-06 section 2.4."""
    lines = ["# Name          HP      AC Gun"]
    for m in state.get("party") or []:
        slot = m.get("slot", 0)
        name = str(m.get("name", ""))[:13].ljust(13)
        hp = "%d/%d" % (m.get("hp", 0), m.get("max_hp", 0))
        cond = {0: "", 1: "U", 2: "D"}.get(m.get("cond", 0), "")
        ac = str(m.get("ac", 0)).ljust(2)
        gun = m.get("gun", "-")
        lines.append("%d %s %s %s %s %s" % (slot, name, hp.ljust(7), cond, ac, gun))
    return lines


def render_frame(data_dir):
    """Render the first frame of a new game (SPEC-06 section 7)."""
    state = headless.first_frame_state(str(data_dir))
    buf = _blank()
    _put(buf, STATUS_ROW, 0, render_status_line(state))
    for j, row in enumerate(render_viewport(state)):
        _put(buf, VIEWPORT_TOP + j, VIEWPORT_LEFT, row)
    for j, line in enumerate(render_party_panel(state)):
        _put(buf, PARTY_TOP + j, PARTY_LEFT, line)
    return buf


def main(data_dir):
    for line in render_frame(data_dir):
        print(line)
    return 0
