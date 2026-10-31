import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(ROOT, "src", "wlengine", "headless.py")
lines = open(p).read().split("\n")
print("TOTAL", len(lines))
for a, b in [(1, 60), (440, 540), (680, 840), (940, 1063)]:
    print("=== lines %d-%d ===" % (a, b))
    for i in range(a - 1, min(b, len(lines))):
        print("%4d| %s" % (i + 1, lines[i]))

print("=== rules.py ===")
p2 = os.path.join(ROOT, "src", "wlengine", "rules.py")
l2 = open(p2).read().split("\n")
for i, s in enumerate(l2):
    print("%4d| %s" % (i + 1, s))

print("=== combat.py ===")
p3 = os.path.join(ROOT, "src", "wlengine", "combat.py")
l3 = open(p3).read().split("\n")
for i, s in enumerate(l3):
    print("%4d| %s" % (i + 1, s))

print("=== labstate.py ===")
p4 = os.path.join(ROOT, "src", "wlengine", "labstate.py")
l4 = open(p4).read().split("\n")
for i, s in enumerate(l4):
    print("%4d| %s" % (i + 1, s))
