from mlib import *
for st in ('mkey','k21'):
    b=Bot(state=SC+'/play/%s.st'%st, out=SC+'/play/run/m3k'+st)
    w=[w for w in b.db.warps((6,8)) if (w[3],w[4])==(26,61)][0]; print(w)
    b.warp((6,8),w[0],w[1]+3); b.wait(80); b.ev(shots=False); b.step('U'); b.wait(30)
    b.step('U'); b.wait(60); b.shot('a'); b.press('A',40); b.clear_text(shots=False); b.step('U'); b.wait(60); b.ev(); b.wait(60); print(st, b.where(), b.log[-2:]); b.shot('b')
