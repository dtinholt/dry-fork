import sys, os, json
sys.path.insert(0, 'SPEC/reference')
import codecs_ref as C, fixtures_gen as FG
DICT = (b" e\x00tanoisrhdlucmfwygpb.,'v!k?\r"
        b"0123456789xjqz:\x0a\x0b\x0c\x0e\x0f\x10\x11\x06/()\"%+;")
SD = 'SPEC/scenario'
scen = json.load(open(os.path.join(SD, 'scenario.json')))
items = json.load(open(os.path.join(SD, 'items.json')))['items']
catalog = {it['id']: it for it in items}
ranks = scen['labstr_tables']['3']['strings']


def conv(c, r):
    if c == 1:
        d = {'messages': r['messages']}
    elif c == 3:
        d = {'visibleDistance': r['visible_distance'], 'hitDistance': r['hit_distance'],
             'message': r['message'], 'groups': r['groups'], 'properName': r['proper_name'],
             'friendly': r['friendly'], 'immobile': r['immobile'], 'npc': 0}
    elif c == 4:
        d = {'message': r['message'], 'impassable': r['impassable'], 'tile': r['tile']}
    elif c == 5:
        d = {'items': r['items'], 'cash': r['cash']}
    elif c == 6:
        d = {'shop': r['shop'], 'message': r['message']}
    elif c == 10:
        d = {k: r[k] for k in ('relative', 'confirm', 'message', 'x', 'y', 'location')}
    elif c == 11:
        d = {'message': r['message']}
    d['newClass'], d['newAction'] = r['new_class'], r['new_action']
    return d


def char_from_json(p, npc):
    a = p['attrs']
    level = p['level']
    hp = 10 + a['STR'] + (level - 1) * (2 + a['STR'] // 5)
    bonus = 0
    if p['armour_slot']:
        bonus = catalog[p['items'][p['armour_slot'] - 1][0]]['damage']
    evasion = dict((s, l) for s, l in p['skills']).get(11, 0)
    c = {'name': p['name'].encode('latin-1'), 'strength': a['STR'], 'intelligence': a['IQ'],
         'luck': a['LCK'], 'speed': a['SPD'], 'agility': a['AGL'], 'dexterity': 0,
         'charisma': a['CHA'], 'money': p['money'], 'gender': p['gender'],
         'nationality': p['nationality'], 'armorClass': a['AGL'] // 5 + bonus + evasion,
         'maxCon': hp, 'curCon': hp, 'weaponSlot': p['weapon_slot'], 'skillPoints': 0,
         'experience': p['xp'], 'level': level, 'armorSlot': p['armour_slot'], 'lastCon': 0,
         'afflictions': 0, 'npc': npc, 'itemRefuse': 0, 'skillRefuse': 0, 'attribRefuse': 0,
         'tradeRefuse': 0, 'joinString': 0, 'willingness': 0,
         'rank': ranks[min(level, 7) - 1].encode('latin-1'), 'gameWon': 0,
         'specialPromotion': 0, 'skills': [list(x) for x in p['skills']],
         'items': [list(x) for x in p['items']]}
    return c


for loc in scen['locations']:
    m = json.load(open(os.path.join(SD, loc['file'])))
    S = loc['size']
    info = m['info']
    mi = {'encounterFrequency': info['encounter_frequency'], 'tileset': info['tileset'],
          'randomMonsterTypes': info['random_monster_types'],
          'maxRandomEncounters': info['max_random_encounters'],
          'borderImage': info['border_image'], 'timePerStep': info['time_per_step'],
          'healRate': info['heal_rate']}
    mobs = []
    for mob in m['mobs']:
        name = mob['name'].encode('latin-1')
        if mob.get('plural_suffix'):
            name += b'\x0a\x0a' + mob['plural_suffix'].encode('latin-1') + b'\x0a'
        md = {'name': name, 'sturdiness': mob['sturdiness'], 'combatRating': mob['combat_rating'],
              'randomDamage': mob['random_damage'], 'maxGroup': mob['max_group'],
              'armorClass': mob['armor_class'], 'fixedDamage': mob['fixed_damage'],
              'weaponType': mob['weapon_type'], 'type': mob['type'], 'portrait': mob['portrait']}
        mobs.append(md)
    mm = {'size': S, 'class': m['action_class'], 'action': m['action_value'],
          'image': [[t + 10 for t in row] for row in m['tiles']],
          'info': mi,
          'actions': {int(c): [conv(int(c), r) for r in recs]
                      for c, recs in m['records'].items() if recs},
          'npcs': [char_from_json(n, 1) for n in m['npcs']],
          'mobs': mobs, 'dictionary': DICT,
          'strings': [s.encode('latin-1') for s in m['strings']]}
    try:
        block, tmo, facts = FG.build_map(mm, 0)
        print(loc['location'], 'OK block', len(block), 'tmo', tmo,
              'prefix', facts['encryptedPrefixLength'])
    except Exception as e:
        import traceback
        print(loc['location'], 'FAIL', type(e).__name__, e)
        traceback.print_exc()
