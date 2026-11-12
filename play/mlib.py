import sys; sys.path.insert(0,'play'); from soko import *
def reach(b):
    k=b.where()[0]; G=b.refresh_grid()
    return k,[(i,w[:2],w[3:]) for i,w in enumerate(b.db.warps(k)) if b.path(*w[:2]) is not None]
def sw(b,x,y):
    b.goto(x,y+1); b.face('U'); b.press('A',60)
    for j in range(5):
        if b.has('はい'): break
        b.press('A',40)
    b.press('A',60); b.clear_text(shots=False); b.wait(30)
def near(b,o): return any(b.path(o[0]+dx,o[1]+dy) is not None for dx,dy in ((0,1),(1,0),(-1,0),(0,-1)))
