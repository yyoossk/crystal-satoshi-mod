from kt import *
from bot import _ok_cell
rom=sys.argv[1]
D={0xA0:('R',-1,0),0xA1:('L',1,0),0xA2:('U',0,1),0xA3:('D',0,-1)}
for mp in sys.argv[2:]:
    b = start(rom, out='kl2_'+mp)
    k=b.mapk(mp); G=grid_of(b.db.r, b.db.maps[k]['hdr']); H,W=len(G),len(G[0])
    hops=[(x,y,G[y][x]) for y in range(H) for x in range(W) if G[y][x] in D]
    print(mp, len(hops), sorted(set(h[2] for h in hops)))
    done=set()
    for x,y,c in hops:
        if c in done: continue
        d,dx,dy=D[c]; sx,sy=x+dx,y+dy
        if not(0<=sx<W and 0<=sy<H) or not _ok_cell(G,sx,sy) or G[sy][sx] in D: continue
        done.add(c)
        b.warp(mp,sx,sy); b.wait(80); b.clear_text()
        s=b.where(); b.step(d); b.wait(20); e=b.where()
        opp={'R':'L','L':'R','U':'D','D':'U'}[d]
        b.step(opp); b.wait(20); f=b.where()
        print(' ', hex(c), 'ledge', (x,y), s[1:], d, '->', e[1:], opp, '->', f[1:])
    b.g.close()
