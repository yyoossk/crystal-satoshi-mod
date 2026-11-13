import functools; print = functools.partial(print, flush=True)
from mlib import *
b=Bot(state=SC+'/play/e4e_r3.st', out=SC+'/play/run/hofsave')
# manual save
b.press('S',40)
for i in range(5): b.press('D',15)
b.press('A',60)
for i in range(8): b.press('A',60)
b.wait(200); b.shot('saved'); b.press('B',30); b.press('B',30)
k=b.where()[0]; print(k)
b.refresh_grid(); ws=[w for w in b.db.warps(k) if w[1]<=2]; print(b.go_warp_xy(ws[0][0],ws[0][1]), b.where())
for i in range(3): b.wait(40); b.ev(shots=False)
for i in range(12):
    if b.objpos(): break
    b.step('U'); b.wait(20); b.ev(shots=False)
o=min(b.objpos(), key=lambda p:p[1])
try:
    print('lance', o, b.talk_to(*o))
    for i in range(8): b.wait(40); b.ev(shots=False)
except KeyError as e: print('credits', e)
for i in range(500):
    b.wait(60)
    if i%25==0: b.shot('w')
for i in range(4): b.press('S',60); b.shot('t%d'%i)
b.press('A',60)
for i in range(10): b.press('A',60)
b.wait(120); print('after continue', b.where()); b.shot('cont'); b.g.save_state(SC+'/play/postjhof.st')
