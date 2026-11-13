import functools; print = functools.partial(print, flush=True)
from mlib import *
b=Bot(state=SC+'/play/e4team.st', out=SC+'/play/run/e4d')
print(b.where(), b.objpos())
b.g.pokes(0xDCA5+2, [0x5E,0x55,0x3A,0x59]); b.g.pokes(0xDCA5+0x17,[15,15,15,15])
k=b.where()[0]
b.refresh_grid(); ws=[w for w in b.db.warps(k) if w[1]<=2]; print(b.go_warp_xy(ws[0][0],ws[0][1]), b.where())
for room in range(2):
    for i in range(3): b.wait(40); b.ev(shots=False)
    k=b.where()[0]
    for i in range(12):
        if b.objpos(): break
        b.step('U'); b.wait(20); b.ev(shots=False)
    b.refresh_grid(); ob=b.objpos(); print('room', k, b.where(), ob)
    o=min(ob, key=lambda p: p[1])
    r=b.talk_to(*o); print(' talk', o, r, b.log[-1:])
    for i in range(8): b.wait(40); b.ev()
    b.g.save_state(SC+'/play/e4d_r%d.st'%room)
    if k==(16,7): break
    b.refresh_grid(); ws=[w for w in b.db.warps(k) if w[1]<=2]
    r=b.go_warp_xy(ws[0][0],ws[0][1]); print(' next', r, b.where(), b.log[-1:])
for i in range(60):
    b.wait(60); b.ev()
    if i%10==0: print(i, b.where())
print('end', b.where())
b.g.save_state(SC+'/play/e4done.st')
