"""LABSTATE.BIN (SPEC-04 LR-57).

Little-endian file: magic ``WLLABSV1``, step counter, day, clock seconds, a
pad byte, the generator state, the cell-change count and the cell changes
sorted by (location, y, x), then a u16 sum of all earlier bytes.
"""

from __future__ import annotations

from .errors import FormatError

MAGIC = b"WLLABSV1"


def encode_labstate(state: dict) -> bytes:
    """LR-57: cell changes written sorted by (location, y, x)."""
    cc = sorted(state.get("cell_changes") or [], key=lambda c: (c[0], c[2], c[1]))
    b = bytearray(MAGIC)
    b += int(state.get("steps", 0)).to_bytes(4, "little")
    b += int(state.get("day", 1)).to_bytes(2, "little")
    b += bytes((int(state.get("seconds", 0)) & 0xFF, 0))
    b += int(state.get("rng_state", 0)).to_bytes(4, "little")
    b += len(cc).to_bytes(2, "little")
    for c in cc:
        b += bytes(int(v) & 0xFF for v in c)
    b += (sum(b) & 0xFFFF).to_bytes(2, "little")
    return bytes(b)


def decode_labstate(data: bytes) -> dict:
    """LR-57; ``FormatError`` on a wrong magic or sum."""
    if len(data) < 0x16 + 2:
        raise FormatError("LABSTATE: %d bytes, too short" % len(data))
    if data[:8] != MAGIC:
        raise FormatError("LABSTATE: bad magic %r" % (bytes(data[:8]),))
    n = int.from_bytes(data[0x14:0x16], "little")
    end = 0x16 + 6 * n
    if len(data) != end + 2:
        raise FormatError("LABSTATE: %d bytes, expected %d" % (len(data), end + 2))
    if sum(data[:end]) & 0xFFFF != int.from_bytes(data[end:end + 2], "little"):
        raise FormatError("LABSTATE: bad checksum")
    cc = [list(data[0x16 + 6 * i:0x16 + 6 * i + 6]) for i in range(n)]
    return {"steps": int.from_bytes(data[8:12], "little"),
            "day": int.from_bytes(data[12:14], "little"),
            "seconds": data[14], "pad": data[15],
            "rng_state": int.from_bytes(data[16:20], "little"),
            "cell_changes": cc}


__all__ = ["encode_labstate", "decode_labstate", "MAGIC"]
