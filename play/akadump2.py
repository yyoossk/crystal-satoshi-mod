import sys, pickle
SC='/tmp/claude-0/-home-claude/e85f874c-51bd-5d2c-9b1a-1d2b8ebf1451/scratchpad'
sys.path.insert(0,SC+'/sameboy-harness/python')
from gr import GR
mp=int(sys.argv[1],16); wi=int(sys.argv[2]); out=sys.argv[3]; path=sys.argv[4]
g=GR(SC+'/akafc/akafc.gbc', state=SC+'/play/rf_room.st'); g.wait(30)
for i in range(6): g.press('B',6,20)
g.pokes(0xD32E,[1,7,wi,mp])
def step(k):
    g.down(k); g.wait(20); g.up(k); g.wait(6)
for i in range(40):
    y,x=g.peek(0xD2E0,2)
    if g.peek(0xD2DD,1)[0]!=0x26: break
    for k in (['U'] if y>1 else [])+(['R'] if x<7 else ['L'] if x>7 else ['U']):
        step(k)
        if g.peek(0xD2E0,2)!=[y,x]: break
import os
for f in [int(x,16) for x in os.environ.get('FLAGS','').split()]:
    a=0xD6C6+(f>>3); g.poke(a, g.peek(a,1)[0] | (1<<(f&7)))
g.wait(200)
def dump(n):
    t0=bytes(g.vpeek(0,0x8000,0x1800)); t1=bytes(g.vpeek(1,0x8000,0x1800))
    tm=bytes(g.vpeek(0,0x9800,0x400)); at=bytes(g.vpeek(1,0x9800,0x400))
    lc=g.peek(0xFF40,1)[0]; sy,sx=g.peek(0xFF42,2)
    pickle.dump({'tm':tm,'at':at,'t0':t0,'t1':t1,'pals':g.pals(),'scx':sx,'scy':sy,'base':0x9800,'lcdc':lc},open(SC+'/out/%s_%02d.pkl'%(out,n),'wb'))
n=0; dump(n)
for k in path:
    if g.peek(0xD2DD,1)[0]!=mp: break
    step(k); g.wait(10); n+=1; dump(n); print(k, g.peek(0xD2E0,2))
print(out, n, hex(g.peek(0xD2DD,1)[0]), g.peek(0xD2E0,2))
