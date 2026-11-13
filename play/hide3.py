import functools; print = functools.partial(print, flush=True)
from mlib import *
b=Bot(state=SC+'/play/hide1.st', out=SC+'/play/run/hide3')
b.face('L'); b.press('A',40)
for i in range(12): b.wait(40); b.ev()
print(b.where(), b.objpos())
b.g.save_state(SC+'/play/hide3.st')
