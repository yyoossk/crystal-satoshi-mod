import functools; print = functools.partial(print, flush=True)
from mlib import *
from story import run
b=Bot(state=SC+'/play/j15b.st', out=SC+'/play/run/j16')
b.refresh_grid(); print(b.objpos())
fl=[o for o in b.objpos() if o!=(2,4)]
if fl: b.talk_to(*fl[0]); [b.ev() for i in range(3)]
run(b, [["talk",2,4,6],["save","j15b2"],["t",[11,2]],["t",[10,2]],["t",[10,3]],["talk",35,9,10],["ev",4],["save","j15c"],["t",[10,4]],["t",[4,9]],["ev",3],["save","j16"]])
print('end', b.where())
