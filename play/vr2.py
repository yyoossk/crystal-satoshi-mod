import functools; print = functools.partial(print, flush=True)
from mlib import *
b=Bot(state=SC+'/play/vr2.st', out=SC+'/play/run/vr2')
SWT={(26,69):[(1,16),(9,16)],(26,70):[(3,5)]}
def info():
    k=b.where()[0]; print('at',b.where(),'reach',reach(b)[1])
    rb=[(o[1],o[2]) for o in b.objs_of(k) if o[0]==90]
    for t in SWT.get(k,[]):
        for bp in rb:
            if bp in b.boulders():
                p=solve(b,bp,t); print('  ',bp,'->',t, p and len(p))
info()
print('push', b.push_to((4,14),(1,16)), b.log[-2:]); b.wait(60); b.ev(shots=False)
info()
b.g.save_state(SC+'/play/vr2a.st')
