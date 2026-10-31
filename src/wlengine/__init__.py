"""wlengine: a clean-room engine for Wasteland (1988, DOS) lab data.

The package is organised by the SPEC sections:

- ``wlengine.errors``     exception hierarchy (SPEC-07 2.12)
- ``wlengine.codecs``     rotating XOR and vertical XOR (SPEC-01 2, 4)
- ``wlengine.huffman``    Huffman bitstreams and msq blocks (SPEC-01 3)
- ``wlengine.strings``    compressed string tables (SPEC-02 9)
- ``wlengine.containers`` containers and records (SPEC-02)
- ``wlengine.graphics``   tilesets, portraits, sprites, font, cursors (SPEC-02)
- ``wlengine.maps``       map blocks (SPEC-03)
- ``wlengine.rules``      game rules (SPEC-04)
- ``wlengine.labstate``   LABSTATE.BIN (SPEC-04 LR-57)
- ``wlengine.scenario``   the scenario compiler (SPEC-05 13)
- ``wlengine.headless``   the headless driver (SPEC-06 5)
- ``wlengine.ui``         the frame renderer (SPEC-06 2)
"""

from __future__ import annotations

__all__ = ["errors", "codecs", "huffman"]

__version__ = "1.0"
