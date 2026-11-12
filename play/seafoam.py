import functools; print = functools.partial(print, flush=True)
import sys; sys.path.insert(0,'play'); from soko import *
b=Bot(state=SC+'/play/k21.st', out=SC+'/play/run/seafoam')
b.setflag(*range(0x23,0x2B)); b.g.poke(0xDCA5+5,0x46); b.g.poke(0xDCA5+0x17+3,15)
F=[(26,63),(26,64),(26,65),(26,66)]
HOLES = {F[0]: [(17, 6), (24, 6)], F[1]: [(18, 6), (23, 6)], F[2]: [(19, 6), (22, 6)], F[3]: [(3, 16), (6, 16)]}
b.warp(F[0],4,16); b.wait(60); b.ev(shots=False)
for fi,k in enumerate(F):
    if fi: 
        r=b.travel(k); print('travel', k, r, b.where(), b.log[-2:])
    b.ev(shots=False); b.wait(30)
    for h in HOLES[k]:
        rb=[(o[1],o[2]) for o in b.objs_of(k) if o[0]==90]
        bs=list(dict.fromkeys(b.boulders()+rb)); print(k,'boulders',bs,'hole',h)
        done=False
        for bp in sorted(bs, key=lambda p: abs(p[0]-h[0])+abs(p[1]-h[1])):
            if bp not in b.boulders():
                for dx,dy in ((0,1),(0,-1),(1,0),(-1,0),(0,2),(2,0)):
                    if b.path(bp[0]+dx,bp[1]+dy) is not None: b.goto(bp[0]+dx,bp[1]+dy); break
            if bp not in b.boulders(): continue
            p=solve(b,bp,h)
            if p is None: continue
            ok=b.push_to(bp,h); b.wait(60); b.ev(shots=False)
            print('  push',bp,'->',h,ok,'now',b.boulders(), b.log[-2:]); b.shot('h'); done=ok; break
        if not done:
            for w in b.db.warps(k):
                b.warp(k,w[0],w[1]); b.wait(60); b.ev(shots=False); b.refresh_grid()
                for bp in [p_ for p_ in bs]:
                    if bp not in b.boulders():
                        for dx,dy in ((0,1),(0,-1),(1,0),(-1,0)):
                            if b.path(bp[0]+dx,bp[1]+dy) is not None: b.goto(bp[0]+dx,bp[1]+dy); break
                    if bp in b.boulders() and solve(b,bp,h):
                        ok=b.push_to(bp,h); b.wait(60); b.ev(shots=False); print('  (from warp',w[:2],') push',bp,'->',h,ok,b.log[-2:]); done=ok; break
                if done: break
        if not done: print('  NO PLAN for hole',h)
    b.g.save_state(SC+'/play/sf%d.st'%fi)
