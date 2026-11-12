"""phase 57: fossils, dojo, eevee, mew"""
from t57 import *
import sys
what = sys.argv[1:]
make_test_rom(SC + '/build/p57.gbc')
out = SC + '/run/t57b'


def act(b, k, x, y, d, tag, n=40):
    for t in range(4):
        b.warp(k, x, y, 150); b.ev(20, shots=False)
        if b.where() == (k, x, y): break
    print('at', b.where()); b.shot(tag+'w'); b.face(d); b.press('A', 40); b.shot(tag+'a')
    fs = []
    for i in range(n):
        if b.in_battle(): break
        if b.has('つけますか'): fs.append(b.shot(tag)); b.press('B', 40); continue
        if b.has('たかさ'): fs.append(b.shot(tag)); b.press('B', 40); continue
        if not b.textbox():
            b.wait(40)
            if not b.textbox(): break
        fs.append(b.shot(tag)); b.press('A', 40)
    return fs


def act2(b, tag, n=40):
    for i in range(n):
        if b.has('つけますか') or b.has('たかさ'): b.shot(tag); b.press('B', 40); continue
        if not b.textbox():
            b.wait(40)
            if not b.textbox(): break
        b.shot(tag); b.press('A', 40)


def party(b):
    b.bank1(); n = b.peek(0xDC9D)[0]; return n, [INV.get(v, v) for v in b.peek(0xDC9E, n)]


if 'fossil' in what:
    b = Bot(state='postjhof2.st', out=out + '/fossil')
    b.setev(0x812); b.clrev(0x813, 0x9bf, 0x9c0, 0x80d, 0x80e)
    act(b, (26, 39), 12, 7, 'U', 'f1')
    print('objs after', b.objpos())
    # second fossil: still there?
    act(b, (26, 39), 13, 7, 'U', 'f2')
if 'dojo' in what:
    b = Bot(state='postjhof2.st', out=out + '/dojo')
    b.g.poke(0xDC9D, 1); b.clrev(0x9d3, 0x9d4, 0x9d5); b.clrev(0x9cc)
    for x, t in ((4, 'lee'), (5, 'chan'), (4, 'lee2')):
        act(b, (25, 3), x, 2, 'U', t); act2(b, t); b.press('B', 30); act2(b, t); print(t, party(b), b.objpos())
if 'eevee' in what:
    b = Bot(state='postjhof2.st', out=out + '/eevee')
    b.g.poke(0xDC9D, 1)
    for i in range(4):
        act(b, (26, 137), 4, 4, 'U', 'e%d' % i); print(i, party(b), b.objpos(), b.peek(0xDA41)[0], b.peek(0xDA3A)[0], b.peek(0xC2DD)[0])
if 'mew' in what:
    b = Bot(state='postjhof2.st', out=out + '/mew')
    for i in range(2):
        act(b, (26, 60), 16, 21, 'U', 'm%d' % i)
        print('battle', b.in_battle(), INV.get(b.peek(W_WILD)[0]), b.peek(0xD25F - 0x31 + 0x31, 1))
        b.shot('mb%d' % i)
        run_away(b); b.shot('mr%d' % i)
    dex = 0xDE2D + 18; b.bank1(); b.g.poke(dex, b.peek(dex)[0] | 0x40)
    act(b, (26, 60), 16, 21, 'U', 'mc'); print('after caught battle', b.in_battle())
