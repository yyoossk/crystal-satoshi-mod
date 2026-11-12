import functools; print = functools.partial(print, flush=True)
import sys; sys.path.insert(0,'play'); from soko import *
b=Bot(state=SC+'/play/k21.st', out=SC+'/play/run/vr')
b.setflag(*range(0x23,0x2B)); b.g.poke(0xDCA5+5,0x46); b.g.poke(0xDCA5+0x17+3,15)
b.warp((26,68),8,16); b.wait(60); b.ev(shots=False)
print(b.where(), b.boulders())
ok=False
for bp in b.boulders():
    p=solve(b,bp,(17,13)); print(bp, p and len(p))
    if p: ok=b.push_to(bp,(17,13)); break
b.wait(60); b.ev(shots=False); b.g.save_state(SC+'/play/vr1.st'); b.refresh_grid(); print('pushed',ok, b.boulders(), b.log[-3:]); b.shot('sw')
G=b.refresh_grid(); print([hex(G[y][x]) for (x,y) in [(8,12),(9,12),(8,13),(9,13)]])
r=b.travel((26,69),maxhops=4); print('to 2F', r, b.where(), b.log[-3:])
b.g.save_state(SC+'/play/vr2.st')
