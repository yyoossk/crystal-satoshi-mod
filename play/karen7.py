import functools; print = functools.partial(print, flush=True)
from mlib import *
b=Bot(state=SC+'/play/karen0.st', out=SC+'/play/run/karen7')
b.talk_to(5,7, n=0)
prev=None
for i in range(300):
    b.g.save_state(SC+'/play/k7_%d.st'%(i%4))
    tm=bytes(b.peek(0xC4A0,360))
    k='A'
    if b.has('だしますか'): k='D'
    b.press(k,30)
    tm2=bytes(b.peek(0xC4A0,360)); pc=b.pc()
    if i%2==0: b.shot('s%03d'%i)
    if b.where()[0][0]>30 or b.peek(0xFF43)[0] not in (0,):
        print('CRASH at', i, pc); b.shot('crash'); break
print('end', b.where(), b.pc())
