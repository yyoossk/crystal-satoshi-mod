import sys; sys.path.insert(0,'play'); from bot import *
sys.path.insert(0,SC+'/tools'); import build_phase15 as P15
b=Bot(state=SC+'/play/k27.st')
r=b.db.r
for n in ['LavenderTown','Route3','Route4','Route25','VermilionPortPassage']:
    k=b.ids[n]; m=b.db.maps[k]; ws=b.db.warps(k)
    x,y=None,None
    # find a walkable tile
    G=grid_of(r,m['hdr'])
    for yy in range(len(G)):
        for xx in range(len(G[0])):
            if G[yy][xx]==0 and x is None: x,y=xx,yy
    b.warp(k,x,y); b.wait(60)
    p=b.peek(P15.W_WARPS_PTR,2); a=p[0]|p[1]<<8; nw=b.peek(P15.W_WARPS_PTR-1)[0]
    o=m['scbank']*0x4000+a-0x4000; ev_a = m['ev']['warps'][0][0] if m['ev']['warps'] else None
    fn=[i for i in range(0x78*0x4000,0x79*0x4000) if r[i]==0x21 and r[i+1]==p[0] and r[i+2]==p[1] and r[i-6]==0xFA]
    print(n,k,'ptr',hex(a),'n',nw,'events-warps-at',hex(ev_a%0x4000+0x4000) if ev_a else None,'fn',[hex(i%0x4000+0x4000) for i in fn])
    print('   alt', r[o:o+5*nw].hex())
    print('   cur', [ (w[0],w[1],w[2],w[3],w[4]) for w in ws])
