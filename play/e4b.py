import functools; print = functools.partial(print, flush=True)
from mlib import *
b=Bot(state=SC+'/play/e4j.st', out=SC+'/play/run/e4run')
for room in range(5):
    for i in range(3): b.wait(40); b.ev(shots=False)
    k=b.where()[0]
    for i in range(12):
        if b.objpos(): break
        b.step('U'); b.wait(20); b.ev(shots=False)
    b.refresh_grid(); ob=b.objpos(); print('room', k, b.where(), ob)
    if not ob: break
    o=min(ob, key=lambda p: p[1]); b.shot('room%d'%room)
    r=b.talk_to(*o); print(' talk', o, r, b.log[-1:])
    for i in range(8): b.wait(40); b.ev()
    b.g.save_state(SC+'/play/e4run_r%d.st'%room)
    if k==(16,7): break
    b.refresh_grid()
    ws=[w for w in b.db.warps(k) if w[1]<=2]
    r=b.go_warp_xy(ws[0][0],ws[0][1]); print(' next', r, b.where(), b.log[-1:])
for i in range(40): b.wait(60); b.ev()
print('end', b.where())
b.g.save_state(SC+'/play/e4run.st')
