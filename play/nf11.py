import sys; sys.path.insert(0,'play')
from t64a import *
from kt import sheet, uniq, seq
ROM=sys.argv[1]
make_test_rom(SC+'/build/%s.gbc'%ROM)
b=Bot(state=SC+'/play/vir_%s.st'%ROM, out=SC+'/run/nf11')
def measure(keys, n):
    m0=b.peek(0xDCB5,2) if False else None
    b.g.down(keys); shown=[]; held=True; k0=b.where()[0]

    for f in range(n):
        b.g.wait(1)
        wy=b.peek(0xFF4A)[0]; shown.append(wy<0x90)
        if held and f%4==0 and b.where()[0]!=k0: b.g.up(keys); held=False
    b.g.up(keys)
    s=''.join('#' if x else '.' for x in shown); return s
for (m,x,y,k) in (('Route1',10,33,'D'),('PalletTown',10,2,'U'),('Route1',10,33,'D'),('ViridianCity',21,33,'D'),('Route1',8,2,'U')):
    b.warp(m,x,y); b.wait(150); b.clear_text(); b.wait(300)
    r=measure(k, 220); print(m, k, b.where(), r.count('#')); print(r)
b.warp('Route1',10,30); b.wait(150); b.clear_text(); b.wait(200)
b.g.down('D'); s=''
for f in range(260):
    b.g.wait(1); s+='#' if b.peek(0xFF4A)[0]<0x90 else '.'
b.g.up('D'); print('walk through', s.count('#'), b.where()); print(s)
