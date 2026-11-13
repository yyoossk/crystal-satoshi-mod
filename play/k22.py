import sys; sys.path.insert(0,'play'); from bot import *
b=Bot(state=SC+'/play/k21.st', out=SC+'/play/run/k22')
b.ev(shots=False)
b.setflag(0x26,0x27)   # rainbow, soul
b.warp((26,31),5,3); b.wait(60); b.shot()
b.goto(3,3); b.ev(); print('7F', b.where(), b.log[-2:])
b.warp((26,35),6,14); b.wait(60); b.shot()
b.goto(6,13); b.ev(); print('11F', b.where(), b.objpos())
b.g.save_state(SC+'/play/k22.st')
