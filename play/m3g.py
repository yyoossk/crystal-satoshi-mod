import sys; sys.path.insert(0,'play'); from soko import *
b=Bot(state=SC+'/play/k21.st', out=SC+'/play/run/m3g')
def reach():
    k=b.where()[0]; G=b.refresh_grid()
    return k,[(i,w[:2],w[3:]) for i,w in enumerate(b.db.warps(k)) if b.path(*w[:2]) is not None]
def sw(x,y):
    b.goto(x,y+1); b.face('U'); b.press('A',60)
    for j in range(5):
        if b.has('はい'): break
        b.press('A',40)
    b.press('A',60); b.clear_text(shots=False); b.wait(30)
b.warp((26,58),6,2); b.wait(60); b.go_warp_xy(6,1); b.ev(shots=False)
print(b.where(), reach(), b.path(10,6) is not None)
b.g.save_state(SC+'/play/m3g.st')
sw(10,5); b.goto(6,2); print('3F sw1', reach())
for i,(x,y),d in reach()[1]:
    if d==(26,57):
        b.go_warp_xy(x,y); b.ev(shots=False); break
print('fell', b.where(), reach())
b.g.save_state(SC+'/play/m3h.st')
if b.where()[0]==(26,57):
    for i,(x,y),d in reach()[1]:
        if d==(26,60): b.go_warp_xy(x,y); b.ev(shots=False); break
    print('B1F', b.where(), reach())
    for o in [(10,2),(1,22),(19,25),(5,4),(5,13)]:
        ok=any(b.path(o[0]+dx,o[1]+dy) is not None for dx,dy in ((0,1),(1,0),(-1,0),(0,-1)))
        print(' ball',o,ok)
    b.g.save_state(SC+'/play/mb1.st')
