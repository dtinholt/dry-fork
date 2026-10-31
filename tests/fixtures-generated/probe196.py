"""Probe 196: dump CP5-pre-save checkpoint vs LABSTATE.BIN, the bump scenario,
and the raider-fight orders scenario.  Run with pytest.

Usage:  pytest tests/fixtures-generated/probe196.py -s -q
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))

import wl_support as W  # noqa: E402
import test_m5_rules as T  # noqa: E402


def _dump(name, obj):
    print("=== %s ===" % name)
    print(json.dumps(obj, indent=1, default=str))


def test_dump_labstate(runner, walkthrough):
    ev, dd = T._saved(runner, walkthrough)
    st = T.ckpt(ev, "CP5-pre-save")
    _dump("checkpoint CP5-pre-save cell_changes", st.get("cell_changes"))
    p = dd / "LABSTATE.BIN"
    print("LABSTATE.BIN exists:", p.is_file(), "size:", p.stat().st_size if p.is_file() else None)
    if p.is_file():
        ls = W.ref_labstate(p.read_bytes())
        _dump("LABSTATE.BIN parsed", ls)
        print("raw bytes:", p.read_bytes()[:64].hex())


def test_dump_bump(runner):
    ev, _ = runner.run("bump", {"seed": T.SEED, "script": ["LEFT"] * 13 + [{"checkpoint": "a"}]})
    _dump("bump events", [T.strip(e) for e in ev])
    print("checkpoint a:", json.dumps(T.ckpt(ev, "a"), default=str))


def test_dump_raider_orders(runner):
    ev, _ = runner.run("raiderfight", {"seed": 3, "script": [{"checkpoint": "a"}]})
    _dump("raiderfight events", [T.strip(e) for e in ev])


def test_dump_ref_labstate():
    """Show the reference LABSTATE.BIN if the oracle can produce one."""
    print("ref_labstate source:")
    import inspect
    print(inspect.getsource(W.ref_labstate))
