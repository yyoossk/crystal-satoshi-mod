import functools; print = functools.partial(print, flush=True)
from mlib import *
b=Bot(state=SC+'/play/karen0.st', out=SC+'/play/run/karen2')
b.talk_to(5,7, n=0)
for i in range(40):
    b.press('A',30)
    if b.in_battle(): break
print('battle', b.in_battle())
for t in range(80):
    tm=b.has('わざタイプ'); ef=b.has('こうかが')
    print(t, b.pc(), 'move' if tm else '', 'noeff' if ef else '', b.in_battle())
    if not b.in_battle(): break
    if t==6: b.g.save_state(SC+'/play/karen1.st')
    b.shot('t%d'%t)
    b.press('A',30)
