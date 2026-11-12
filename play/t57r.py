from t57 import *
import sys
make_test_rom(SC + '/build/p57.gbc')
b = Bot(state='postjhof2.st', out=SC + '/run/t57r')
k = (21, 4)
G = grid_of(b.db.r, b.db.maps[k]['hdr'])
spot = None
for y in range(1, len(G) - 1):
    for x in range(len(G[0])):
        if G[y][x] in (0x00,) and G[y - 1][x] == 0x29: spot = (x, y); break
    if spot: break
print('spot', spot)
for t in range(4):
    b.warp(k, *spot, 120)
    if b.where()[0] == k: break
print(b.where())
b.giveitem(PM.ITEM['SUPER_ROD'])
b.face('U'); b.shot('pos')
b.press('S', 40); b.shot('menu')
res = []
for trial in range(6):
    b.ev(40, shots=False)
    if b.where() != (k, *spot):
        b.warp(k, *spot, 120); b.ev(40, shots=False)
    b.face('U')
    b.press('S', 40); b.press('D', 20); b.press('D', 20); b.press('A', 60)
    b.press('R', 40); b.press('R', 40)
    for j in range(30): b.press('D', 8)
    b.press('U', 20)
    b.shot('sel'); b.press('A', 40); b.shot('sub'); b.press('A', 200); b.shot('fish')
    sp = None
    for j in range(30):
        if b.in_battle():
            b.wait(60); b.bank1(); sp = INV.get(b.peek(W_WILD)[0]); b.shot('bt'); run_away(b); break
        if b.textbox(): b.shot('tx'); b.press('A', 40)
        else: b.wait(30)
        if not b.textbox() and not b.in_battle() and j > 3: break
    res.append(sp); print(trial, sp, flush=True)
    b.wait(random.randint(5, 80))
