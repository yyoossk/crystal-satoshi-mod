import functools; print = functools.partial(print, flush=True)
from mlib import *
b=Bot(state=SC+'/play/j03.st', out=SC+'/play/run/j04')
print(b.objs_of(), b.objpos())
b.talk_to(3,5)
for i in range(8): b.wait(40); b.ev()
print(b.where(), b.objpos())
b.g.save_state(SC+'/play/j04.st')
