import functools; print = functools.partial(print, flush=True)
from mlib import *
import bot as B
b=Bot(state=SC+'/play/j13b.st', out=SC+'/play/run/j14')
b.setev(0x29, 0x10, 0x6e9, 0x6f3, 0x6f4); b.giveitem(0xF3); b.g.poke(0xDCA5+5, 0x0F)
B.CAN_CUT[0]=True
for t in [(8,7),(11,22),(3,52),(11,23),(11,1),(11,2)]:
    for hop in range(20):
        if b.where()[0]==t: break
        b.refresh_grid(); b.travel(t, maxhops=1); b.ev(shots=False)
    print(t, b.where(), b.log[-2:])
b.g.save_state(SC+'/play/j14.st')
