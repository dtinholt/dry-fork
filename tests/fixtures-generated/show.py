import sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
name = sys.argv[1] if len(sys.argv) > 3 else "dump110.txt"
a = int(sys.argv[-2]); b = int(sys.argv[-1])
lines = open(os.path.join(HERE, name)).read().split("\n")
for i in range(a - 1, min(b, len(lines))):
    print("%5d| %s" % (i + 1, lines[i]))
