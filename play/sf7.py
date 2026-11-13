import functools; print = functools.partial(print, flush=True)
from mlib import *
for st in ('sf6','sf3'):
    b=Bot(state=SC+'/play/%s.st'%st, out=SC+'/play/run/sf7'+st)
    b.g.poke(0xDCA5+4,0x39); b.g.poke(0xDCA5+0x17+2,15)
    if st=='sf3': b.warp((26,67),7,10); b.wait(60)
    print(st, b.where(), b.boulders())
    b.refresh_grid(); print(b.goto(7,11), b.where())
    b.face('D'); b.press('A',60); b.shot('s1')
    for i in range(6):
        if b.has('はい'): break
        b.press('A',40); b.shot('s')
    b.press('A',60); b.shot('s2'); b.clear_text(shots=False)
    for i in range(3): b.step('D'); b.wait(20)
    b.wait(60); print(st,'after', b.where()); b.shot('end')
