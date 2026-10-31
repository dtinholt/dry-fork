"""Exception hierarchy of the engine (SPEC-07 section 2.12).

Every decoder and loader raises ``FormatError`` (or ``ChecksumError``) for
malformed input, never another exception type.
"""

from __future__ import annotations


class FormatError(ValueError):
    """Malformed input: a bad header, a size mismatch, a truncated buffer."""


class ChecksumError(FormatError):
    """A checksum stored in the data does not match the computed one."""


class ScriptError(Exception):
    """A malformed headless script (SPEC-06 5.1, exit code 4)."""


class RepeatLimitError(ScriptError):
    """A ``repeat_until`` exceeded its ``max`` (SPEC-06 5.1, exit code 2)."""


__all__ = ["FormatError", "ChecksumError", "ScriptError", "RepeatLimitError"]
