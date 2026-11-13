import functools; print = functools.partial(print, flush=True)
from mlib import *
b=Bot(state=SC+'/play/nb0.st', out=SC+'/play/run/j01')
print(b.where(), b.objpos())
r=b.travel((24,5)); print('lab', r, b.where(), b.log[-2:])
for i in range(6): b.wait(40); b.ev()
print(b.where(), b.objpos(), [o for o in b.objs_of()])
b.g.save_state(SC+'/play/j01.st')
