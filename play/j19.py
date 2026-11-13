import functools; print = functools.partial(print, flush=True)
from mlib import *
from story import run
import bot as B
b=Bot(state=SC+'/play/j18b.st', out=SC+'/play/run/j19')
b.g.poke(0xDCA5+4, 0x39); b.g.poke(0xDCA5+0x17+2, 15); b.g.poke(0xDCA5+5, 0x0F)   # Surf + Cut
B.CAN_CUT[0]=True; B.CAN_SURF[0]=True
run(b, [["t",[1,12]],["t",[1,13]],["t",[1,14]],["save","j19a"],["t",[3,47]],["talk",8,8,6],["save","j19b"],
        ["t",[1,14]],["t",[22,1]],["t",[22,2]],["t",[22,3]],["save","j19c"],["t",[22,5]],["talk",4,1,10],["save","j19d"],
        ["t",[22,3]],["t",[22,7]],["talk",2,3,6],["save","j19e"]])
print([hex(v) for v in b.peek(0xD84A,2)])
