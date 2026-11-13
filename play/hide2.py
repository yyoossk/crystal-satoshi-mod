import functools; print = functools.partial(print, flush=True)
from mlib import *
b=Bot(state=SC+'/play/hide1.st', out=SC+'/play/run/hide2')
b.step('D'); b.wait(30)
for i in range(10): b.wait(40); b.ev()
print(b.where(), b.objpos())
b.g.save_state(SC+'/play/hide2.st')
