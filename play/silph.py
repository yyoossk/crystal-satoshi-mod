import sys; sys.path.insert(0,'play'); sys.path.insert(0,'tools'); from bot import *
import build_phase14 as P
b=Bot(state=SC+'/play/k21.st', out=SC+'/play/run/silph')
pn={l.split()[0]:tuple(map(int,l.split()[1].split(':'))) for l in open(SC+'/play/portnames.txt')}
WALK=(0x00,0x01,0x02,0x03,0x04,0x05,0x06,0x07,0x08,0x09,0x0a,0x0b,0x0c,0x0d,0x0e,0x0f)
res=[]
for f in range(2,12):
    n='SilphCo%dF'%f; k=pn[n]
    G=grid_of(b.db.r,b.db.maps[k]['hdr'])
    for (bx,by,blk) in P.doors_of(n):
        X,Y=2*bx,2*by; done=False
        for (sx,sy,d,ix,iy) in [(X,Y-1,'D',X,Y),(X,Y+2,'U',X,Y+1),(X-1,Y,'R',X,Y),(X+2,Y,'L',X+1,Y),(X+1,Y-1,'D',X+1,Y),(X,Y+3,'U',X,Y+2)]:
            if not(0<=sy<len(G) and 0<=sx<len(G[0])) or G[sy][sx]!=0: continue
            b.g.load_state(SC+'/play/k21.st'); b.wait(3)
            b.warp(k,sx,sy); b.wait(40)
            # without key: try to walk in
            b.step(d); p0=b.where()
            if p0[1:]!=(sx,sy): continue  # walked in? means no door here
            b.face(d); b.press('A',40); ng=b.has('だめ'); b.clear_text(shots=False)
            b.giveitem(P.SILPH_CARD_KEY)
            b.face(d); b.press('A',60); ok=b.has('ロック'); b.clear_text(shots=False); b.wait(30)
            b.step(d); b.wait(20); p1=b.where()
            res.append((n,(bx,by),(sx,sy),d,'ng' if ng else '-', 'ok' if ok else '-', p1[1:]))
            print(res[-1]); b.shot(n); done=True; break
        if not done: print(n,(bx,by),'no stand pos'); res.append((n,(bx,by),'nostand'))
