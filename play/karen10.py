import functools; print = functools.partial(print, flush=True)
from mlib import *
import numpy as np
b=Bot(state=SC+'/play/karen0.st', out=SC+'/play/run/karen10')
orig=b.press; cnt=[0]; blk=[0]; last=[b'']
def press(k, w=30):
    cnt[0]+=1
    b.g.save_state(SC+'/play/k10_%d.st'%(cnt[0]%30))
    t=bytes(b.peek(0xC4A0,360))
    if t==last[0]: blk[0]+=1
    else: blk[0]=0
    last[0]=t
    if blk[0]>=10 or b.where()[0][0]>30:
        print('BLANK at', cnt[0], b.pc()); raise SystemExit
    orig(k, w)
b.press=press
r=b.talk_to(5,7); print('talk', r)
for i in range(8): b.wait(40); b.ev()
print('end', b.where())
