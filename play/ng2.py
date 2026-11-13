import sys; sys.path.insert(0,'play')
from t64a import *
rom=sys.argv[1]; tag=sys.argv[2]
make_test_rom(SC+'/build/%s.gbc'%rom)
b=Bot(out=SC+'/run/ng_'+tag)
b.wait(400)
assert b.until_text('サトシ'); b.shot('m1')
b.press('D'); b.press('A',60); b.shot('m2')
r=b.until_text('ョン',w=20); b.shot('m3'); assert r
b.press('D'); b.press('A',60); b.shot('m4')
for i in range(30):
    b.press('A',40)
b.shot('end'); print(b.where())
b.g.save_state(SC+'/play/ng_%s.st'%tag)
b.sheet('a')
