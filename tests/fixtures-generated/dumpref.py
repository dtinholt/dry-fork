import json
import sys
d = json.load(open('SPEC/scenario/walkthrough-reference-log.json'))
ev = d['events']
lo = int(sys.argv[1]) if len(sys.argv) > 1 else 0
hi = int(sys.argv[2]) if len(sys.argv) > 2 else 40
for i, e in enumerate(ev[lo:hi], lo):
    print(i, json.dumps(e)[:260])
