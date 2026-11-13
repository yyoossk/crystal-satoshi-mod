import functools; print = functools.partial(print, flush=True)
from mlib import *
b=Bot(state=SC+'/play/j02b.st', out=SC+'/play/run/j03b')
for tgt in [(24,3),(26,3),(26,1)]:
    r=b.travel(tgt); print(tgt, r, b.where(), b.log[-2:])
    for i in range(4): b.wait(30); b.ev(shots=False)
b.g.save_state(SC+'/play/j03a.st')
import glob,os
for f in glob.glob(SC+'/play/run/j03b/*'): os.remove(f)
r=b.travel((26,10)); print(r)
for i in range(10): b.wait(40); b.ev()
print(b.where(), b.objpos(), b.peek(0xDC9D,5))
b.g.save_state(SC+'/play/j03.st')
