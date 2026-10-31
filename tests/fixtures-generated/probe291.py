"""probe291: focused introspection of headless.run, Engine start, scenario.load."""
import inspect
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from wlengine import headless, scenario  # noqa: E402

print("=== headless.run ===")
print(inspect.getsource(headless.run))

for n in ("new_game", "start", "start_new_game", "reset", "run_script", "play"):
    fn = getattr(headless.Engine, n, None)
    if fn is not None:
        print("=== Engine.%s ===" % n)
        print(inspect.getsource(fn))

print("=== scenario.load ===")
print(inspect.getsource(scenario.load))
print("=== Scenario.__init__ ===")
print(inspect.getsource(scenario.Scenario.__init__))
