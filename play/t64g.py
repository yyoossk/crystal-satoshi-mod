from t64a import *
import bot
def water_spot(b, k):
    G = bot.grid_of(b.db.r, b.db.maps[k]['hdr'])
    H,W=len(G),len(G[0])
    for y in range(H):
        for x in range(W):
            if G[y][x]==0x00:
                for dx,dy,d in ((1,0,'R'),(-1,0,'L'),(0,1,'D'),(0,-1,'U')):
                    X,Y=x+dx,y+dy
                    if 0<=X<W and 0<=Y<H and G[Y][X] in (0x29,0x20,0x21):
                        return x,y,d
def fish(b, k, item, n=6, tag='f'):
    x,y,d = water_spot(b,k)
    b.warp(k,x,y); b.wait(60); b.clear_text(shots=False); b.face(d)
    res=[]
    for i in range(n):
        # use the item via a script: callasm UseItem? -> simply: Start, bag
        b.press('S',40); b.press('D',15); b.press('D',15); b.press('A',60)
        b.shot(tag+'bag')
        return
