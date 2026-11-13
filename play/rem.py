import functools; print = functools.partial(print, flush=True)
from mlib import *
for gym,leader,w in [((14,4),(5,1),'pewter'),((17,8),None,'fuchsia'),((23,4),(5,3),'viridian')]:
    b=Bot(state=SC+'/play/k27.st', out=SC+'/play/run/rem_'+w)
    b.setev(0x44)
    ws=[x for x in b.db.warps(gym)]
    b.warp(gym, ws[0][0], ws[0][1]-1); b.wait(60); b.ev(shots=False)
    b.refresh_grid()
    if leader is None:
        cand=[o for o in b.objs_of(gym)]; print(cand); leader=(cand[0][1],cand[0][2])
    r=b.talk_to(*leader); print(w, r, b.where(), b.log[-2:])
    for i in range(3): b.ev()
