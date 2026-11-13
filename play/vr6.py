import functools; print = functools.partial(print, flush=True)
from mlib import *
b=Bot(state=SC+'/play/vr4.st', out=SC+'/play/run/vr6')
b.refresh_grid(); r=b.go_warp_xy(2,0); b.ev(shots=False); print(r, b.where(), reach(b), b.boulders())
k=b.where()[0]
rb=[(o[1],o[2]) for o in b.objs_of(k) if o[0]==90]
for bp in list(dict.fromkeys(b.boulders()+rb)):
    for t in [(1,16),(9,16)]:
        if bp in b.boulders(): print(bp,t, solve(b,bp,t) and 'ok')
b.g.save_state(SC+'/play/vr6.st')
