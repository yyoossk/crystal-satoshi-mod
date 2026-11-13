import functools; print = functools.partial(print, flush=True)
from mlib import *
b=Bot(state=SC+'/play/karen0.st', out=SC+'/play/run/karen9')
orig=b.press; cnt=[0]
def press(k, w=30):
    cnt[0]+=1
    b.g.save_state(SC+'/play/k9_%d.st'%(cnt[0]%6))
    s=b.peek(0xFF43)[0]; ww=b.where()
    if ww[0][0]>30:
        print('BAD before press', cnt[0], k, s, ww, b.pc()); raise SystemExit
    orig(k, w)
b.press=press
r=b.talk_to(5,7); print('talk', r)
for i in range(8): b.wait(40); b.ev()
print('end', b.where())
