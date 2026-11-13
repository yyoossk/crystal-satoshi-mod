import functools; print = functools.partial(print, flush=True)
from mlib import *
from story import run
b=Bot(state=SC+'/play/j17a.st', out=SC+'/play/run/j18')
for d in 'DDDDD': b.step(d); b.wait(20)
b.face('D'); b.press('A',40); b.ev()
for i in range(4): b.wait(40); b.ev()
print(b.where(), b.objpos())
b.refresh_grid(); print(b.go_warp_xy(7,15), b.where()); b.ev()
run(b, [["t",[4,9]],["ev",3],["t",[4,7]],["talk",5,1,12],["save","j18"]])
print([hex(v) for v in b.peek(0xD84A,2)])
