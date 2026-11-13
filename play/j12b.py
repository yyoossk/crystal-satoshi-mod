import functools; print = functools.partial(print, flush=True)
from mlib import *
b=Bot(state=SC+'/play/j12a.st', out=SC+'/play/run/j12b')
import shutil; shutil.rmtree(SC+'/play/run/j12b', ignore_errors=True); import os; os.makedirs(SC+'/play/run/j12b')
b.travel((10,10)); b.ev(); b.refresh_grid(); print(b.talk_to(4,3)); [b.ev() for i in range(6)]; print('aide', b.where(), b.peek(0xDC9D,7))
for t in [(10,5),(10,1),(3,37),(8,6),(8,7)]:
    for hop in range(30):
        if b.where()[0]==t: break
        b.refresh_grid(); r=b.travel(t, maxhops=1); print(' hop', b.where(), b.log[-2:])
    print(t, b.where())
b.g.save_state(SC+'/play/j12b.st')
