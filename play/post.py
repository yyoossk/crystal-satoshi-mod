import functools; print = functools.partial(print, flush=True)
from mlib import *
b=Bot(state=SC+'/play/e4e_r4.st', out=SC+'/play/run/post')
for i in range(120):
    b.press('A',60)
    g,m=b.peek(0xDC7B,2)
    if i%10==0: b.shot('c'); print(i, (g,m))
    if (g,m) in b.db.maps and not b.in_battle() and i>40:
        b.wait(120); print('map', b.where()); break
for i in range(10): b.wait(40); b.ev()
print(b.where(), b.objpos())
b.g.save_state(SC+'/play/post0.st')
