import functools; print = functools.partial(print, flush=True)
from mlib import *
b=Bot(state=SC+'/play/karen0.st', out=SC+'/play/run/karen8')
b.talk_to(5,7, n=0)
for i in range(40):
    if b.in_battle(): break
    b.press('A',30)
print('in battle', b.in_battle())
k=0; noeff=False; hist=[]
while k<400:
    b.g.save_state(SC+'/play/k8_%d.st'%(k%5))
    if b.has('こうかが') or b.has('のこりポイント'): noeff=True
    act=[]
    if b.has('だしますか'):
        act=['D','A','A']
    elif noeff and b.has('わざタイプ') and not b.has('のこりポイント'):
        act=['D','A']; noeff=False
    else:
        act=['A']
    if k%7==6: act.append('B')
    for a in act: b.press(a,30 if a!='D' else 20)
    hist.append((k,act))
    k+=1
    scx=b.peek(0xFF43)[0]; w=b.where()
    if w[0][0]>30 or scx not in (0,):
        print('BAD', k, act, scx, w, b.pc()); b.shot('bad'); break
    if not b.in_battle(): print('battle over', k, w); break
print(hist[-6:])
