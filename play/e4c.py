import functools; print = functools.partial(print, flush=True)
from mlib import *
b=Bot(state=SC+'/play/e4run_r3.st', out=SC+'/play/run/e4c')
print(b.where(), b.objpos()); b.shot('a')
b.refresh_grid(); print(b.path(4,2), b.path(5,2))
for i in range(12):
    if b.where()[0]!=(16,6): break
    b.step('U'); b.wait(20); b.ev(shots=False); print(b.where())
b.shot('b')
