import functools; print = functools.partial(print, flush=True)
from mlib import *
b=Bot(state=SC+'/play/vr4d.st', out=SC+'/play/run/vr4')
exec(open(SC+'/play/vr2.py').read().split("b=Bot")[1].split("\ninfo()")[0].split('\n',1)[1])
b.refresh_grid()
print('push', b.push_to((6,1),(3,5)), b.log[-3:]); b.wait(60); b.ev(shots=False); info()
b.g.save_state(SC+'/play/vr4.st')
for hop in range(8):
    k=b.where()[0]
    if k==(16,1): break
    b.refresh_grid()
    r=b.travel((16,1),maxhops=1); print('hop', r, b.where(), b.log[-2:])
print('end', b.where())
b.g.save_state(SC+'/play/vr5.st')
