import json
d = json.load(open('SPEC/scenario/map1-saltwell.json'))
ac = d['action_class']
t = d['tiles']
for y in range(32):
    row = []
    for x in range(32):
        if ac[y][x] != 0:
            row.append((x, ac[y][x], t[y][x]))
    print(y, row)
