import sys, random, functools; print = functools.partial(print, flush=True)
import sys; sys.path.insert(0,'play'); from soko import *
b=Bot(state=SC+'/play/k21.st', out=SC+'/play/run/mansion')
M1,M2,M3,MB=(26,57),(26,58),(26,59),(26,60)
SW={M1:[(2,5)],M2:[(2,11)],M3:[(10,5)],MB:[(20,3),(18,25)]}
# secret key ball on B1F
key=[o for o in b.objs_of(MB) if o[0]==0x54]; print('balls B1F', key)
b.warp(M1,5,26); b.wait(60); b.ev(shots=False)
visited=set(); prevk=None; sw=0; got=False; seen_maps=set()
def bag_has(item):
    # key items pocket JP: scan memory for item id is unreliable; use event of ball flag instead
    return False
for it in range(80):
    k=b.where()[0]; G=b.refresh_grid(); seen_maps.add((k,sw))
    if k==MB:
        for o in key:
            if b.path(o[1],o[2]+1) is not None or b.path(o[1]+1,o[2]) is not None or b.path(o[1]-1,o[2]) is not None or b.path(o[1],o[2]-1) is not None:
                print('key reachable', o); b.talk_to(o[1],o[2]); b.ev(); got=True; break
        if got: break
    cands=[]
    for i,w in enumerate(b.db.warps(k)):
        if (k,i,sw) in visited or (w[3],w[4]) not in (M1,M2,M3,MB): continue
        if b.path(w[0],w[1]) is not None: cands.append(('w',i,w))
    for (sx,sy) in SW.get(k,[]):
        if (k,'s',sx,sy,sw) not in visited and b.path(sx,sy+1) is not None: cands.append(('s',(sx,sy),None))
    if not cands: print('stuck', b.where(), sw); break
    def pri(c):
        if c[0]=='w': return 2 if tuple(c[2][3:5])==prevk else 0
        return 1
    cands.sort(key=pri); c=cands[0]
    if c[0]=='w':
        i,w=c[1],c[2]; visited.add((k,i,sw)); prevk=k; r=b.go_warp_xy(w[0],w[1]); b.ev(shots=False)
        print('warp',k,i,(w[0],w[1]),'->',b.where(), r)
    else:
        sx,sy=c[1]; visited.add((k,'s',sx,sy,sw)); b.goto(sx,sy+1); b.face('U'); b.press('A',60)
        for j in range(5):
            if b.has('はい'): break
            b.press('A',40)
        b.press('A',60); b.clear_text(shots=False); sw^=1; b.shot('sw'); print('switch',k,(sx,sy),'->',sw)
        visited=set(v for v in visited)  # keep
print('got key', got, b.where(), b.log[-4:])
b.g.save_state(SC+'/play/mansion.st')
