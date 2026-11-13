import functools; print = functools.partial(print, flush=True)
from mlib import *
b=Bot(state=SC+'/play/vr4.st', out=SC+'/play/run/vr7')
b.refresh_grid(); b.go_warp_xy(23,7); b.ev(shots=False); print(b.where())
b.refresh_grid(); b.go_warp_xy(23,7); b.ev(shots=False); print(b.where())
b.refresh_grid()
if (24,10) not in b.boulders(): b.goto(24,8)
print(b.boulders(), solve(b,(24,10),(23,15)))
print(b.push_to((24,10),(23,15)), b.log[-2:]); b.wait(60); b.ev(shots=False)
b.refresh_grid(); r=b.go_warp_xy(23,15); b.ev(shots=False); print('fell', r, b.where(), b.boulders())
b.refresh_grid()
for bp in b.boulders():
    p=solve(b,bp,(9,16)); print(bp,'->9,16', p and len(p))
    if p: print(b.push_to(bp,(9,16)), b.log[-2:]); break
b.wait(60); b.ev(shots=False); print(reach(b))
b.g.save_state(SC+'/play/vr7.st')
for hop in range(6):
    if b.where()[0]==(16,1): break
    b.refresh_grid(); r=b.travel((16,1),maxhops=1); print('hop', r, b.where(), b.log[-2:])
print('end', b.where()); b.shot('end')
b.g.save_state(SC+'/play/vr8.st')
