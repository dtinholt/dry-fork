# Review reply 1 (session, 17:3x CDT, 21 Oct 2026)

M1 and M2 at 100 % in one iteration: good. Three notes, nothing to redo.

1. Keep going exactly as your worklog plan says: wlengine.maps with decode_map, the lab-rule
   helpers, load_map through LABTABLES.BIN, then run M3 and read only the first differing field
   in each failure. The map spec's section 9 (lab rules v1) is the authority for action
   semantics; where it says UNKNOWN, do not invent, the tests do not reach there.
2. Your worklog is the only memory between iterations. Before you end an iteration, write
   three lines: what passes, what the next failing test needs, and any spec sentence you had
   to interpret. Keep it short; the tail is what the next iteration sees.
3. For M4, read SPEC-05 section 13 and SPEC-07's API for wlengine.scenario.compile before
   writing code, and reuse your own encoders from codecs.py and containers.py. Do not read or
   import anything under SPEC/reference at runtime; the tests refuse it.
