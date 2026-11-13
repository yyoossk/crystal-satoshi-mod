import functools; print = functools.partial(print, flush=True)
from mlib import *
import glob,os
b=Bot(state=SC+'/play/j05.st', out=SC+'/play/run/j05')
for tgt in [(24,3),(24,4),(24,5)]:
    r=b.travel(tgt); print(tgt, r, b.where(), b.log[-2:])
    for i in range(6): b.wait(30); b.ev()
    if b.where()[0]!=tgt:
        r=b.travel(tgt); print(' again', r, b.where())
for i in range(10): b.wait(40); b.ev()
print(b.where(), b.objpos())
b.g.save_state(SC+'/play/j05.st')
