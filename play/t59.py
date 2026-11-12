from t57b import party, INV
from t57 import *
from lib import mapid
make_test_rom(SC + '/build/p59.gbc')
b = Bot(state='postjhof2.st', out=SC + '/run/t59')
b.g.poke(0xDC9D, 1); b.giveitem(0x36)
k = mapid('CeladonGameCornerPrizeRoom'); print(k)
for t in range(4):
    b.warp(k, 4, 2, 120)
    if b.where()[0] == k: break
b.bank1(); b.g.pokes(0xD848, [0x27, 0x0F]); print('coins', b.peek(0xD848, 2))
b.face('U')
def seq(keys):
    for c in keys: b.press(c, 50); b.shot(c)
b.press('A', 40)
for i in range(20):
    if b.has('ケーシィ'): break
    b.press('A', 50)
b.wait(40)
for c in 'DDD': b.g.press(c, 8, 40)
b.press('A', 60); b.shot('p2')
for i in range(20):
    if b.has('ストライク'): break
    b.wait(30)
b.wait(40); b.shot('menu2'); b.g.press('D', 8, 40); b.press('A', 60); b.shot('ask')
b.press('A', 60)
for i in range(10):
    if b.has('つけますか'): b.press('B', 40)
    else: b.press('A', 40)
    b.shot('y')
    if b.has('ストライク'): break
b.shot('back'); b.press('B', 40); b.press('B', 40); b.press('B', 40)
b.bank1(); print(party(b), 'coins', b.peek(0xD848, 2))
