import functools; print = functools.partial(print, flush=True)
from mlib import *
b=Bot(state=SC+'/play/sf4.st', out=SC+'/play/run/sf5')
b.refresh_grid()
print('c', solve(b,(5,14),(4,14))); print(b.push_to((5,14),(4,14)), b.log[-2:])
print('b', solve(b,(8,14),(6,16))); print(b.push_to((8,14),(6,16)), b.log[-2:])
b.wait(60); b.ev(shots=False); print(b.where(), b.boulders())
b.g.save_state(SC+'/play/sf5.st')
# now B4F: currents should be blocked
r=b.travel((26,67)); print('B4F', r, b.where(), b.log[-3:]); b.shot('b4')
for i in range(4): b.wait(60); b.ev()
print(b.where())
b.g.save_state(SC+'/play/sf6.st')
