import functools; print = functools.partial(print, flush=True)
from mlib import *
b=Bot(state=SC+'/play/postjhof2.st', out=SC+'/play/run/elmt')
for i in range(4): b.wait(60); b.ev()
r=b.travel((24,5)); b.ev(); print(r, b.where(), b.objpos())
b.refresh_grid(); print(b.talk_to(5,2))
for i in range(6): b.wait(40); b.ev()
