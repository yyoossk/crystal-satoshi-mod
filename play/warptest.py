import sys,os; sys.path.insert(0,'play')
from bot import *
from mapdb import DB, crystal_names
make_test_rom(SC+'/build/'+os.environ.get('ROMN','p110')+'.gbc')
db=DB(SC+'/build/p110.gbc'); nm=crystal_names()
keys=[eval(a) for a in sys.argv[1:]] if len(sys.argv)>1 else [k for k in sorted(db.maps) if k[0]==26]
b=Bot(state=SC+'/play/pt_s46.st', out=SC+'/run/wt'); b.wait(10)
b.g.save_state(SC+'/play/wt_base.st')
D={'U':(0,-1),'D':(0,1),'L':(-1,0),'R':(1,0)}
bad=[]
for k in keys:
    G=grid_of(db.r, db.maps[k]['hdr']); H=len(G); W=len(G[0])
    seen=set()
    for w in db.warps(k):
        x,y=w[0],w[1]
        if (x,y) in seen: continue
        seen.add((x,y))
        res=None
        for d,(dx,dy) in D.items():
            sx,sy=x-dx,y-dy
            if not(0<=sx<W and 0<=sy<H) or G[sy][sx]!=0: continue
            b.g.load_state(SC+'/play/wt_base.st'); b.wait(2)
            b.warp(k,sx,sy,wait=90)
            if b.where()[0]!=k or b.where()[1:]!=(sx,sy): continue
            b.step(d); b.wait(40)
            cd={0x70:'D',0x76:'L',0x78:'U',0x7e:'R'}.get(G[y][x], d)
            if b.where()[0]==k: b.step(cd); b.wait(40)
            ok=b.where()[0]!=k
            res=(d, ok)
            if ok: break
        print(k, nm.get(k), (x,y), hex(G[y][x]), res, flush=True)
        if res and not res[1]: bad.append((k,(x,y)))
print('BAD', bad)
