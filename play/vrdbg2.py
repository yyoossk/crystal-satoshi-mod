import sys; sys.path.insert(0,'play'); from soko import *
b=Bot(state=SC+'/play/k21.st', out=SC+'/play/run/vrdbg2')
b.setflag(*range(0x23,0x2B)); b.g.poke(0xDCA5+5,0x46)
b.warp((26,68),8,16); b.wait(60); b.ev(shots=False)
b.step('D'); b.wait(30); print(b.where()); b.step('R'); b.wait(30); print(b.where()); b.shot()
b.step('U'); b.wait(30); print(b.where()); b.shot()
