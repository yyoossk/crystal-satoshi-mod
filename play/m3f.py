import sys; sys.path.insert(0,'play'); from soko import *
b=Bot(state=SC+'/play/k21.st', out=SC+'/play/run/m3f')
def reach(k):
    G=b.refresh_grid()
    ws=[(i,w[:2],w[3:]) for i,w in enumerate(b.db.warps(k)) if b.path(*w[:2]) is not None]
    return ws
for k,(x,y),sws in [((26,58),(5,11),[(2,11)]),((26,59),(7,11),[(10,5)]),((26,57),(5,11),[(2,5)])]:
    b.g.load_state(SC+'/play/k21.st'); b.wait(3)
    b.warp(k,x,y); b.wait(60)
    print(k,'sw0', reach(k), [s for s in sws if b.path(s[0],s[1]+1) is not None])
    # toggle by pressing switch via script: set flag? use bg event if reachable
    for s in sws:
        if b.path(s[0],s[1]+1) is not None:
            b.goto(s[0],s[1]+1); b.face('U'); b.press('A',60)
            for j in range(5):
                if b.has('はい'): break
                b.press('A',40)
            b.press('A',60); b.clear_text(shots=False); b.wait(30)
            b.goto(x,y)
            print(k,'sw1', reach(k)); b.shot(str(k[1]))
