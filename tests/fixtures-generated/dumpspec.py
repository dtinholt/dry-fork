import re
txt = open('SPEC/SPEC-05-scenario.md').read()
i = txt.index('### 5.2 Saltwell')
j = txt.index('```text', i)
k = txt.index('```', j + 7)
block = txt[j + 7:k]
for line in block.splitlines():
    print(repr(line))
