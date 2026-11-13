import functools; print = functools.partial(print, flush=True)
from mlib import *
b=Bot(state=SC+'/play/post0.st', out=SC+'/play/run/post2')
b.shot('home')
w=[w for w in b.db.warps((24,4)) if (w[3],w[4])==(24,5)][0]
b.warp((24,4), w[0], w[1]+1); b.wait(60); b.ev(shots=False)
b.step('U'); b.wait(60); b.ev()
b.refresh_grid(); print(b.where(), b.objpos())
r=b.talk_to(5,2); print(r)
for i in range(6): b.wait(40); b.ev()
b.g.save_state(SC+'/play/post2.st')
