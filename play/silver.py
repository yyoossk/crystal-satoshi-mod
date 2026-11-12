import functools; print = functools.partial(print, flush=True)
from mlib import *
b=Bot(state=SC+'/play/postjhof2.st', out=SC+'/play/run/silver')
b.warp((3,76),9,31); b.wait(80); b.ev(shots=False)
print(b.where(), b.objpos(), b.objs_of((3,76)))
b.refresh_grid(); r=b.talk_to(9,10); print('talk', r, b.log[-2:])
for i in range(10): b.wait(40); b.ev()
print(b.where())
b.g.save_state(SC+'/play/silver.st')
