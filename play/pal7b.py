import sys; sys.path.insert(0,'play')
from t64a import *
ROM=sys.argv[1]
make_test_rom(SC+'/build/%s.gbc'%ROM)
b=Bot(state=SC+'/play/vir_%s.st'%ROM, out=SC+'/run/pal7')
def p7(): return b.g.pals().split()[0][3:][7*16:8*16]
for m,x,y,k in (('NewBarkTown',2,8,'L'),('Route1',10,33,'D')):
    b.warp(m,x,y); b.wait(400); b.clear_text(); b.wait(200)
    print(m,'idle',p7(), hex(b.peek(0xFF4A)[0]))
    b.g.down(k)
    for f in range(120):
        b.g.wait(1)
        if b.peek(0xFF4A)[0]<0x90: print(' sign',p7(), b.where()); b.shot('sign'+m); break
    b.g.up(k); b.wait(300)
    b.press('S',30); print(' menu', p7()); b.press('B',30)
