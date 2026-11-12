import functools; print = functools.partial(print, flush=True)
from mlib import *
b=Bot(state=SC+'/play/hide0.st', out=SC+'/play/run/jjc')
b.refresh_grid(); b.go_warp_xy(7,3); b.wait(60); b.shot('hideout'); print(b.where(), b.objpos())
b=Bot(state=SC+'/play/j12c.st', out=SC+'/play/run/jjc')
b.travel((8,7)); b.travel((3,40)); b.ev(shots=False); b.goto(15,14); b.wait(30); b.shot('well'); print(b.where(), b.objpos())
b=Bot(state=SC+'/play/k22.st', out=SC+'/play/run/jjc')
b.warp((26,35),7,13); b.wait(80); b.shot('silph'); print(b.where(), b.objpos())
