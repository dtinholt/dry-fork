import sys, os, shutil, tempfile, json
sys.path.insert(0, "src")
from wlengine import headless, rules

dd = tempfile.mkdtemp()
shutil.copytree("tests/fixtures-generated/dd", dd, dirs_exist_ok=True)
eng = headless.Engine(dd, seed=20261021, options={})
eng.new_game(20261021)
print("skill_table type", type(eng.sc.skill_table))
print("tbl[14]", eng.sc.skill_table[14] if 14 in eng.sc.skill_table else "MISSING")
print("skill_attribute(14)", eng.skill_attribute(14))
print("attr_value(m3,14)", eng.attr_value(eng.party[2], 14))
print("pick_member(14)", eng.pick_member(14))
print("check_need(2,15,30)", rules.check_need(2, 15, 30))
