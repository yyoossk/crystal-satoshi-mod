import functools; print = functools.partial(print, flush=True)
from mlib import *
b=Bot(state=SC+'/play/vr2a.st', out=SC+'/play/run/vr3')
exec(open(SC+'/play/vr2.py').read().split("b=Bot")[1].split("\ninfo()")[0].split('\n',1)[1])
b.refresh_grid(); r=b.go_warp_xy(23,7); print(r, b.log[-4:], b.path(23,7)); b.ev(shots=False); info()
b.g.save_state(SC+'/play/vr3.st')
