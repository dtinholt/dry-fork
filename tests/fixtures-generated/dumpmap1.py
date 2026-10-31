import json
d = json.load(open('SPEC/scenario/map1-saltwell.json'))
print('conventions', json.dumps(d.get('conventions'), indent=1)[:1500])
print('action_cells', json.dumps(d.get('action_cells'))[:2000])
print('info', json.dumps(d.get('info')))
print('width/height', d.get('width'), d.get('height'))
print('tileset', d.get('tileset'))
