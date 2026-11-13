import functools; print = functools.partial(print, flush=True)
from mlib import *
b=Bot(state=SC+'/play/j02b.st', out=SC+'/play/run/j03')
for tgt in [(24,3),(26,3),(26,1),(26,10)]:
    r=b.travel(tgt); print(tgt, r, b.where(), b.log[-2:])
    for i in range(4): b.wait(30); b.ev(shots=False)
for i in range(6): b.wait(40); b.ev()
print(b.where(), b.objpos())
b.g.save_state(SC+'/play/j03.st')
