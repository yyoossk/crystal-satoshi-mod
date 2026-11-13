import sys; sys.path.insert(0,'play'); from soko import *
b=Bot(state=SC+'/play/k21.st', out=SC+'/play/run/vrdbg')
b.setflag(*range(0x23,0x2B)); b.g.poke(0xDCA5+5,0x46)
b.warp((26,68),5,14); b.wait(60); b.ev(shots=False)
b.face('D'); b.press('A',60); print(b.has('おせる'))
for i in range(5): b.press('A',40); b.shot('t')
print(b.where(), b.boulders())
b.clear_text(shots=False); b.wait(30)
for i in range(2):
    b.g.down('D')
    for j in range(12): b.wait(4); print(i,j*4, b.where(), b.boulders())
    b.g.up('D'); b.wait(60); print(b.where(), b.boulders())
