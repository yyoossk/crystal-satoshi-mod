import functools; print = functools.partial(print, flush=True)
from mlib import *
b=Bot(state=SC+'/play/hide3.st', out=SC+'/play/run/radio')
b.script([0x33, 1743&255, 1743>>8, 0x33, 1745&255, 1745>>8, 0x32, 1742&255, 1742>>8, 0x33, 1744&255, 1744>>8], 30)
b.warp((11,2),5,16); b.wait(60); b.ev(shots=False)
b.step('U'); b.wait(60); b.ev(shots=False); print('1F', b.where(), b.objpos())
for i in range(10):
    if b.where()[0]==(3,18): break
    b.refresh_grid(); b.travel((3,18), maxhops=1); b.ev(shots=False)
print('2F', b.where(), b.objpos())
b.g.save_state(SC+'/play/radio2f.st')
b.refresh_grid(); r=b.talk_to(13,2); print('jj', r, b.log[-2:])
for i in range(10): b.wait(40); b.ev()
print(b.where(), b.objpos())
