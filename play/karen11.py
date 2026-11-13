import functools; print = functools.partial(print, flush=True)
from mlib import *
import json
b=Bot(state=SC+'/play/karen0.st', out=SC+'/play/run/karen11')
orig=b.press; cnt=[0]; log=[]; rec=[False]
ocmd=b.g.cmd
def cmd(c):
    if rec[0] and not c.startswith(('peek','shot','save','pc','wpeek','vpeek','oam','pals')): log.append(c)
    ocmd(c)
b.g.cmd=cmd
def press(k, w=30):
    cnt[0]+=1
    if cnt[0]==30:
        b.g.save_state(SC+'/play/k11_30.st'); rec[0]=True
    if b.where()[0][0]>30 or (cnt[0]>30 and 'sp=6a' in b.pc()):
        json.dump(log, open(SC+'/play/k11_log.json','w')); print('CRASH', cnt[0], len(log)); raise SystemExit
    orig(k, w)
b.press=press
r=b.talk_to(5,7); print('talk', r)
for i in range(8): b.wait(40); b.ev()
json.dump(log, open(SC+'/play/k11_log.json','w')); print('end', b.where(), cnt[0], len(log))
