import functools; print = functools.partial(print, flush=True)
from mlib import *
b=Bot(state=SC+'/play/j05.st', out=SC+'/play/run/j06')
for i in range(6): b.step('U'); b.wait(30); b.ev(); print(b.where(), b.objpos())
for i in range(10):
    b.wait(40); b.ev()
    if b.has('ニックネーム') or b.has('なまえは'):
        pass
print(b.where(), b.objpos()); b.shot('end')
b.g.save_state(SC+'/play/j06.st')
