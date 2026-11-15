import sys, os; sys.path.insert(0,'play')
from bot import *
make_test_rom(SC+'/build/'+os.environ.get('ROMN','p110')+'.gbc')
st=sys.argv[1]; N=int(sys.argv[2])
b=Bot(state=SC+'/play/%s.st'%st, out=SC+'/run/turbo'); b.wait(20)
k,x,y=b.where(); print(k,x,y)
g=b.g
ref=g.vpeek(0,0x8000,0xC0)
import os
os.environ
g.cmd('watch d4c3 1')
def turbo(frames, dirkey=None):
    for f in range(frames//4):
        if dirkey: g.down(dirkey)
        g.down('A'); g.wait(2); g.up('A'); g.wait(2)
    if dirkey: g.up(dirkey)
bad=0
for it in range(N):
    turbo(64,'L'); turbo(64,'R')
    g.cmd('wmark it%d'%it)
    if it==int(os.environ.get('SAVEAT','-1')): g.save_state(SC+'/play/turbo_at.st')
    if it%5==0:
        b.bank1(); o0=b.peek(0xD4C9,4); o1=b.peek(0xD4C9+0x28,0x14)
        pl=b.peek(0xD4C9+0x10,4)
        if o0[1:4]!=[0,0,0x0b] or (o1[0]==0xe2 and abs(o1[0x12]-pl[2])+abs(o1[0x13]-pl[3])>2): print('BAD', it, o0, pl, o1[0x12:0x14])
        v=g.vpeek(0,0x8000,0xC0)
        b.bank1()
        if v!=ref and not b.in_battle():
            bad+=1; b.shot('diff%d'%it); g.save_state(SC+'/play/turbo_%d.st'%it); print('diff at', it, b.where())
            ref=v
print('done', b.where(), bad)
b.shot('end')
