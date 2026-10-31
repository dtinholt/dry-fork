import json
import re

txt = open('SPEC/SPEC-05-scenario.md').read()
i = txt.index('### 5.2 Saltwell')
j = txt.index('```text', i)
k = txt.index('```', j + 7)
block = txt[j + 7:k]
rows = {}
for line in block.splitlines():
    m = re.match(r'^\s*(\d+)\s+\|(.*)\|\s*$', line)
    if m:
        rows[int(m.group(1))] = m.group(2)
print('rows', len(rows))
d = json.load(open('SPEC/scenario/map1-saltwell.json'))
ac = d['action_class']
t = d['tiles']
# spec blocked chars
BLOCK = set('#|')
for y in sorted(rows):
    spec = rows[y]
    if len(spec) != 32:
        print('bad row', y, len(spec), repr(spec))
        continue
    specblock = [1 if c in BLOCK else 0 for c in spec]
    jsonblock = [1 if ac[y][x] == 11 else 0 for x in range(32)]
    if specblock != jsonblock:
        print('y=%d mismatch' % y)
        print('  spec', ''.join(str(b) for b in specblock))
        print('  json', ''.join(str(b) for b in jsonblock))
