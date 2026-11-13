import functools; print = functools.partial(print, flush=True)
from mlib import *
b=Bot(state=SC+'/play/e4team.st', out=SC+'/play/run/karen')
b.g.pokes(0xDCA5+2, [0x5E,0x55,0x3A,0x59]); b.g.pokes(0xDCA5+0x17,[10,15,15,10])
k=b.where()[0]
b.refresh_grid(); ws=[w for w in b.db.warps(k) if w[1]<=2]; b.go_warp_xy(ws[0][0],ws[0][1])
for i in range(3): b.wait(40); b.ev(shots=False)
for i in range(12):
    if b.objpos(): break
    b.step('U'); b.wait(20); b.ev(shots=False)
print(b.where(), b.objpos())
b.g.save_state(SC+'/play/karen0.st')
