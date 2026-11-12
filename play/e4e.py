import functools; print = functools.partial(print, flush=True)
from mlib import *
b=Bot(state=SC+'/play/e4team2.st', out=SC+'/play/run/e4e')
b.g.pokes(0xDCA5+2, [0x5E,0x55,0x3A,0x59]); b.g.pokes(0xDCA5+0x17,[10,15,15,10])
for room in range(5):
    for i in range(3): b.wait(40); b.ev(shots=False)
    k=b.where()[0]
    for i in range(12):
        if b.objpos(): break
        b.step('U'); b.wait(20); b.ev(shots=False)
    b.refresh_grid(); ob=b.objpos(); print('room', k, b.where(), ob)
    if not ob: break
    o=min(ob, key=lambda p: p[1])
    r=b.talk_to(*o); print(' talk', o, r, b.log[-1:])
    for i in range(8): b.wait(40); b.ev()
    print(' after', b.where(), b.peek(0xDC9D,7))
    b.g.save_state(SC+'/play/e4e_r%d.st'%room)
    if k==(16,7): break
    b.refresh_grid(); ws=[w for w in b.db.warps(k) if w[1]<=2]
    r=b.go_warp_xy(ws[0][0],ws[0][1]); print(' next', r, b.where(), b.log[-1:])
for i in range(60):
    b.wait(60); b.ev()
    if i%10==0: print(i, b.where())
print('end', b.where())
b.g.save_state(SC+'/play/e4done.st')
