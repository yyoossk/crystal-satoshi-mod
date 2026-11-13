import functools; print = functools.partial(print, flush=True)
from mlib import *
b=Bot(state=SC+'/play/e4e_r4.st', out=SC+'/play/run/post3')
# credits: press nothing, just wait and A slowly until title
for i in range(400):
    b.wait(60)
    t=b.tilemap()
    if i%20==0: b.shot('w')

b.shot('t0')
for i in range(6): b.press('S',60); b.shot('t%d'%(i+1))
