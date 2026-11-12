import functools, sys; print = functools.partial(print, flush=True)
from mlib import *
make_test_rom(SC + '/build/p63.gbc')
caught = 'caught' in sys.argv
b = Bot(state=SC + '/play/e4e_r3.st', out=SC + '/play/run/t63' + ('c' if caught else ''))
b.bank1(); b.g.poke(0xD836, 1)
if caught:
    v = b.peek(0xDE2D + 31)[0]; b.g.poke(0xDE2D + 31, v | 4)
print('before', b.peek(0xD836, 1))
k = b.where()[0]
b.refresh_grid(); ws = [w for w in b.db.warps(k) if w[1] <= 2]; b.go_warp_xy(ws[0][0], ws[0][1])
for i in range(3): b.wait(40); b.ev(shots=False)
for i in range(12):
    if b.objpos(): break
    b.step('U'); b.wait(20); b.ev(shots=False)
o = min(b.objpos(), key=lambda p: p[1])
try:
    print('lance', o, b.talk_to(*o))
    for i in range(8): b.wait(40); b.ev(shots=False)
except KeyError as e: print('credits', e)
for i in range(500): b.wait(60)
for i in range(4): b.press('S', 60)
b.press('A', 60)
for i in range(10): b.press('A', 60)
b.wait(120); b.bank1(); print('after HoF + continue', b.where(), 'd836', b.peek(0xD836, 1), 'beatE4', b.flag(0x44))
b.g.save_state(SC + '/play/t63' + ('c' if caught else '') + '.st')
