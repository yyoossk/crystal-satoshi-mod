import sys; sys.path.insert(0,'.')
from t57 import *
make_test_rom(SC+'/build/p64.gbc')
b=Bot(sav=SC+'/play/p64nb.sav', out=SC+'/run/base2')
b.wait(400)
for i in range(3): b.press('A',60)
for i in range(8): b.press('A',90)
b.wait(120)
print('day hour', set_tod(b,1))
b.g.poke(0xDC9D,0); b.g.poke(0xDC9E,0xFF)
for sp,lv in ((4,24),(25,22),(1,22),(7,22),(17,24),(12,20)):
    b.script([0x2D, sp, lv, 0, 0], 120)
    for i in range(6):
        b.press('B',40)
        if not b.textbox(): break
b.bank1(); b.g.poke(0xD833,0)
b.warp((24,4),10,9); b.wait(100)
b.step('D'); b.wait(30); b.g.shot(SC+'/run/base2.png')
b.g.save_state(SC+'/play/blogbase2.st')
