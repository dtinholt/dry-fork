"""Acceptance-test configuration for PREREG-W1 (SPEC-07).

- Registers the `milestone(name)` marker; every test carries exactly one.
- Adds `--group M1` ... `--group M6` to select one milestone group.
- Puts the project's src/ first on sys.path so `import wlengine` finds the
  builder's package.
- Provides the session fixtures: the SPEC-02/SPEC-03 fixture set, the engine's
  compiled Dry Fork data, the oracle decoding of that data, and cached headless
  runs.

Frozen with the tests (SPEC-07 section 6).
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

sys.dont_write_bytecode = True
_TESTS = Path(__file__).resolve().parent
_SRC = _TESTS.parent / "src"
for p in (str(_TESTS), str(_SRC)):
    if p in sys.path:
        sys.path.remove(p)
sys.path.insert(0, str(_TESTS))
sys.path.insert(0, str(_SRC))

import wl_support as W  # noqa: E402

MILESTONES = ("M1", "M2", "M3", "M4", "M5", "M6")
sys.addaudithook(W.audit_hook)


def pytest_addoption(parser):
    parser.addoption("--group", action="store", default=None, metavar="M",
                     help="run only the tests of one milestone group (M1 to M6), SPEC-07")


def pytest_configure(config):
    config.addinivalue_line("markers", "milestone(name): PREREG-W1 milestone group, M1 to M6 (SPEC-07)")


def pytest_collection_modifyitems(config, items):
    group = config.getoption("--group")
    if group is not None and group not in MILESTONES:
        raise pytest.UsageError("--group must be one of %s, got %r" % (", ".join(MILESTONES), group))
    keep, drop = [], []
    for it in items:
        marks = [m.args[0] if m.args else None for m in it.iter_markers("milestone")]
        if len(marks) != 1 or marks[0] not in MILESTONES:
            raise pytest.UsageError("%s must carry exactly one milestone marker (got %r)" % (it.nodeid, marks))
        (keep if group is None or marks[0] == group else drop).append(it)
    if drop:
        config.hook.pytest_deselected(items=drop)
        items[:] = keep


# ---------------------------------------------------------------------------
# Session fixtures
# ---------------------------------------------------------------------------

def _oracle(args: list[str], timeout: int = 300) -> subprocess.CompletedProcess:
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    env.pop("PYTHONPATH", None)
    return subprocess.run([sys.executable, str(_TESTS / "oracle_tool.py")] + args, capture_output=True,
                          text=True, timeout=timeout, env=env, stdin=subprocess.DEVNULL)


class FixtureSet:
    def __init__(self, d: Path, manifest: dict) -> None:
        self.dir = d
        self.manifest = manifest

    def path(self, name: str) -> str:
        return str(self.dir / name)

    def read(self, name: str) -> bytes:
        return (self.dir / name).read_bytes()


def _make_fixture_set(tmp_path_factory, seed: int) -> FixtureSet:
    d = tmp_path_factory.mktemp("fixtures")
    mand = tmp_path_factory.mktemp("manifest")
    r = _oracle(["fixtures", str(d), str(mand), str(seed)])
    if r.returncode != 0:
        raise RuntimeError("fixture generator failed (test infrastructure): %s %s" % (r.stdout[-500:], r.stderr[-500:]))
    W.FORBIDDEN_PREFIXES.append(str(mand) + os.sep)
    return FixtureSet(d, json.loads((mand / "manifest.json").read_text()))


@pytest.fixture(scope="session")
def fixture_set(tmp_path_factory) -> FixtureSet:
    """SPEC-02 section 12.8 / SPEC-03 section 12 fixtures (seed 19880101), manifest kept apart."""
    return _make_fixture_set(tmp_path_factory, 19880101)


@pytest.fixture(scope="session")
def fixture_set_alt(tmp_path_factory) -> FixtureSet:
    """The same generator with seed 20261022: same structure, different content (SPEC-07 section 5)."""
    return _make_fixture_set(tmp_path_factory, 20261022)


class Compiled:
    def __init__(self, d: Path | None, error: str | None) -> None:
        self.dir = d
        self.error = error

    def need(self) -> Path:
        if self.error:
            W.fail("scenario compile failed, so this check cannot run: " + self.error)
        return self.dir

    def copy(self, tmp_path_factory) -> Path:
        src = self.need()
        dst = tmp_path_factory.mktemp("data")
        shutil.copytree(src, dst, dirs_exist_ok=True)
        return dst


@pytest.fixture(scope="session")
def compiled(tmp_path_factory) -> Compiled:
    """The engine's own compilation of SPEC/scenario (SPEC-05 section 13)."""
    d = tmp_path_factory.mktemp("compiled")
    try:
        W.engine_ready()
        fn = W.api("scenario.compile")
    except pytest.fail.Exception as e:
        return Compiled(None, str(e))
    try:
        W._armed(fn, str(W.SCENARIO), str(d), allow_reference_log=True)
    except NotImplementedError as e:
        return Compiled(None, "wlengine.scenario.compile: not implemented (%s)" % (e or "NotImplementedError"))
    except Exception as e:  # noqa: BLE001
        return Compiled(None, "wlengine.scenario.compile raised %s: %s" % (type(e).__name__, W.short(str(e), 200)))
    if W._STATE["violations"]:
        v = W._STATE["violations"][0]
        W._STATE["violations"].clear()
        if not v.startswith(str(W.SCENARIO)):
            return Compiled(None, "wlengine.scenario.compile opened a file the engine must not read: %s" % v)
    return Compiled(d, None)


class OracleView:
    def __init__(self, data: dict | None, error: str | None) -> None:
        self.data = data or {}
        self.error = error

    def oracle(self, section: str):
        if self.error:
            W.fail(self.error)
        errs = self.data.get("errors", {})
        if section in errs:
            W.fail("reference reader rejected the compiled data (%s): %s" % (section, errs[section]))
        if section not in self.data.get("oracle", {}):
            W.fail("reference reader found no %s in the compiled data" % section)
        return self.data["oracle"][section]

    def expected(self, section: str):
        if self.error and not self.data.get("expected"):
            W.fail(self.error)
        return self.data["expected"][section]


@pytest.fixture(scope="session")
def oracle_view(compiled) -> OracleView:
    if compiled.error:
        return OracleView(None, "scenario compile failed, so this check cannot run: " + compiled.error)
    r = _oracle(["compiled", str(compiled.dir), str(W.SCENARIO)])
    try:
        data = json.loads(r.stdout)
    except ValueError:
        raise RuntimeError("oracle tool failed (test infrastructure): %s" % r.stderr[-800:])
    if "fatal" in data:
        raise RuntimeError("oracle tool failed (test infrastructure): %s" % data["fatal"][-800:])
    return OracleView(data, None)


@pytest.fixture(scope="session")
def expected_view(tmp_path_factory) -> dict:
    """Expected structures from the scenario JSON alone (no engine involved)."""
    d = tmp_path_factory.mktemp("empty")
    r = _oracle(["compiled", str(d), str(W.SCENARIO)])
    data = json.loads(r.stdout)
    if "fatal" in data:
        raise RuntimeError("oracle tool failed (test infrastructure): %s" % data["fatal"][-800:])
    return data["expected"]


class Runner:
    """Cached headless runs on fresh copies of the compiled data."""

    def __init__(self, compiled: Compiled, tmp_path_factory) -> None:
        self.compiled = compiled
        self.tpf = tmp_path_factory
        self.cache: dict = {}

    def run(self, key: str, script: dict, seed: int | None = None, data_dir: Path | None = None):
        """Return (events, data_dir). Fails the test cleanly on any engine problem."""
        ck = (key, seed, str(data_dir) if data_dir else None)
        if ck in self.cache:
            ev, dd, err = self.cache[ck]
            if err:
                W.fail(err)
            return ev, dd
        dd = data_dir or self.compiled.copy(self.tpf)
        err = None
        ev = None
        try:
            ev = W.call("headless.run", str(dd), json.loads(json.dumps(script)), seed)
            if not isinstance(ev, list) or not all(isinstance(e, dict) for e in ev):
                err = "wlengine.headless.run must return a list of event dicts, got %s" % type(ev).__name__
        except pytest.fail.Exception as e:
            err = str(e)
        self.cache[ck] = (ev, dd, err)
        if err:
            W.fail(err)
        return ev, dd


@pytest.fixture(scope="session")
def runner(compiled, tmp_path_factory) -> Runner:
    return Runner(compiled, tmp_path_factory)


@pytest.fixture(scope="session")
def walkthrough() -> dict:
    return W.load_json(W.SCENARIO / "walkthrough.json")


@pytest.fixture(scope="session")
def reference_log() -> list[dict]:
    return W.load_json(W.REFERENCE_LOG)["events"]
