from t57 import *
import sys
make_test_rom(SC + '/build/p57.gbc')
res = {}
EXP37 = {64: 43808, 67: 43808, 75: 43808, 93: 43808}
for sp_, ev in ((64, 'ALAKAZAM'), (75, 'GOLEM'), (93, 'GENGAR')):
    b = Bot(state='postjhof2.st', out=SC + '/run/t57e/%d' % sp_)
    b.g.poke(0xDC9D, 0); b.givepoke(sp_, 36)
    e = EXP37[sp_] - 1; b.bank1(); b.g.pokes(0xDCA5 + 8, [e >> 16, (e >> 8) & 255, e & 255]); b.g.pokes(0xDCA5 + 2, [0x21, 0x21, 0x21, 0x21]); b.g.pokes(0xDCA5 + 0x17, [30, 30, 30, 30])
    print(sp_, b.peek(0xDC9D, 3), b.peek(0xDCA5 + 0x1F)[0])
    for t in range(4):
        b.warp((13, 1), 12, 22, 120)
        if b.where()[0] == (13, 1): break
    for i in range(200):
        b.step('R'); b.step('L')
        if b.textbox() and not b.in_battle(): b.ev(40, shots=False)
        if b.in_battle(): break
    for i in range(200):
        b.press('A', 40)
        if i % 10 == 0: b.shot()
        if not b.in_battle() and not b.textbox():
            b.wait(60)
            if not b.textbox() and not b.in_battle(): break
    b.shot('end'); b.bank1()
    print(sp_, 'now', INV.get(b.peek(0xDC9E)[0]), 'lv', b.peek(0xDCA5 + 0x1F)[0], flush=True)
    b.g.close()
