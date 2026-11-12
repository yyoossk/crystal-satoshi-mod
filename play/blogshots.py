import sys; sys.path.insert(0,'.')
from t64a import *
import bot
make_test_rom(SC+'/build/p64.gbc')
OUTD=SC+'/run/blog/maps2'
def open_spot(b,k,pref=None):
    G=bot.grid_of(b.db.r,b.db.maps[k]['hdr']); H,W=len(G),len(G[0])
    objs={(o[1],o[2]) for o in b.objs_of(k)}
    best=None
    cy,cx=(H//2,W//2) if pref is None else pref
    for y in range(2,H-3):
        for x in range(2,W-2):
            ok=all(G[y+dy][x+dx]==0 and (x+dx,y+dy) not in objs for dy in range(-1,4) for dx in range(-1,2))
            if ok:
                d=(y-cy)**2+(x-cx)**2
                if best is None or d<best[0]: best=(d,x,y)
    return best
def shoot(b,name,pref=None):
    k=b.ids[name]; s=open_spot(b,k,pref)
    if not s: print('no spot',name); return
    _,x,y=s
    b.warp(k,x,y); b.wait(80); b.clear_text(shots=False)
    b.step('D'); b.step('D'); b.wait(40)
    b.g.shot(OUTD+'/'+name+'.png'); print(name,(x,y),b.where())
if __name__=='__main__':
    import os; os.makedirs(OUTD,exist_ok=True)
    b=Bot(state='blogbase2.st', out=OUTD+'/x')
    for n in sys.argv[1:]: shoot(b,n)
