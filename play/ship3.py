import functools; print = functools.partial(print, flush=True)
from mlib import *
b=Bot(state=SC+'/play/ship2.st', out=SC+'/play/run/ship3')
b.goto(2,28); print(b.where(), b.objpos())
r=b.talk_to(2,25); print('girl', r, b.log[-2:])
for i in range(10): b.wait(60); b.ev()
print('after', b.where(), b.objpos())
b.g.save_state(SC+'/play/ship3.st')
