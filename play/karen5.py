import functools; print = functools.partial(print, flush=True)
from mlib import *
b=Bot(state=SC+'/play/karen0.st', out=SC+'/play/run/karen5')
b.talk_to(5,7, n=0)
hist=[]
for i in range(400):
    w=b.where()
    tm=bytes(b.peek(0xC4A0+12*20, 6*20))
    if w[0]==(16,6) or b.in_battle(): b.g.save_state(SC+'/play/karen_last%d.st'%(i%3))
    hist.append((i,w,b.pc()))
    if w[0] not in ((16,6),(16,7)) and not b.in_battle():
        print('LEFT', i, w); break
    k='A'
    if b.has('こうかが') or b.has('のこりポイント'): k='D'
    b.press(k,30)
    if i%3==0: b.shot('s')
print(hist[-6:])
