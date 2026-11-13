import functools; print = functools.partial(print, flush=True)
from mlib import *
b=Bot(state=SC+'/play/j06.st', out=SC+'/play/run/j07')
b.press('S',40); b.press('A',60)
for i in range(10): b.wait(40); b.ev()
print(b.where(), b.objpos()); b.shot('end')
b.g.save_state(SC+'/play/j07.st')
