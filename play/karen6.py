import functools; print = functools.partial(print, flush=True)
from mlib import *
b=Bot(state=SC+'/play/karen0.st', out=SC+'/play/run/karen6')
r=b.talk_to(5,7); print('talk', r, b.where(), b.in_battle())
for i in range(8): b.wait(40); b.ev()
print(b.where(), b.objpos(), b.pc())
b.g.save_state(SC+'/play/karen6.st')
