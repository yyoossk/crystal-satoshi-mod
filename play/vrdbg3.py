import sys; sys.path.insert(0,'play'); import soko; from soko import *
b=Bot(state=SC+'/play/k21.st', out=SC+'/play/run/vrdbg3')
b.setflag(*range(0x23,0x2B)); b.g.poke(0xDCA5+5,0x46)
b.warp((26,68),8,16); b.wait(60); b.ev(shots=False)
plan=solve(b,(5,15),(17,13))[:5]
orig=soko.solve; soko.solve=lambda s,bp,t: plan
print(b.push_to((5,15),(9,16)), b.where(), b.boulders())
b.g.save_state(SC+'/play/vr_carpet.st')
print(b.goto(9,17), b.where())
b.shot('a')
b.g.down('U')
for j in range(12): b.wait(6); print(j, b.where(), b.boulders())
b.g.up('U'); b.wait(40); b.shot('b'); print(b.where(), b.boulders())
