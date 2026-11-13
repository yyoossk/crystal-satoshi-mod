import sys; sys.path.insert(0,'play')
from t64a import *
make_test_rom(SC+'/build/p70.gbc')
b=Bot(state=SC+'/play/vir_p70.st', out=SC+'/run/sign')
fs=[]
for m,x,y,k in (('Route1',10,33,'D'),('NewBarkTown',2,8,'L')):
    b.warp(m,x,y); b.wait(300); b.clear_text(); b.wait(200)
    b.g.down(k)
    for f in range(160):
        b.g.wait(1)
        if b.peek(0xFF4A)[0]<0x90 and f>30: b.g.wait(20); fs.append(b.shot()); break
    b.g.up(k); b.wait(60)
b.press('A',30); fs.append(b.shot())
from kt import sheet; sheet(fs, SC+'/run/sign.png', W=3, scale=2)
