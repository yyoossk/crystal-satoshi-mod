import functools; print = functools.partial(print, flush=True)
from mlib import *
import sys
st, out, rising = sys.argv[1], sys.argv[2], sys.argv[3]=='1'
b=Bot(state=SC+'/play/%s.st'%st, out=SC+'/play/run/'+out)
if rising: b.g.poke(0xD84A, 0xFF)
b.warp((16,2),5,12); b.wait(60); b.ev(shots=False)
b.refresh_grid(); b.go_warp_xy(14,3); b.wait(60)
for room in range(5):
    for i in range(4): b.wait(40); b.ev()
    k=b.where()[0]; b.refresh_grid(); ob=b.objpos(); print('room', k, b.where(), ob)
    if not ob: break
    o=min(ob, key=lambda p: p[1]); b.shot('room%d'%room)
    r=b.talk_to(*o); print(' talk', o, r, b.log[-1:])
    for i in range(6): b.wait(40); b.ev()
    b.g.save_state(SC+'/play/%s_r%d.st'%(out,room))
    if room==0 and not rising and len(sys.argv)>4: break
    b.refresh_grid()
    ws=[w for w in b.db.warps(k) if w[1]<=2]
    if not ws: break
    r=b.go_warp_xy(ws[0][0],ws[0][1]); print(' next', r, b.where(), b.log[-1:])
for i in range(30): b.wait(60); b.ev()
print('end', b.where())
b.g.save_state(SC+'/play/%s.st'%out)
