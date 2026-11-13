import sys; sys.path.insert(0,'play'); from bot import *
b=Bot(state=SC+'/play/k19.st', out=SC+'/play/run/k20')
b.ev(shots=False)
b.warp('Route12',10,60); b.wait(60); b.shot()
b.talk_to(10,62)
print(b.where(), b.objpos(), b.log[-3:])
b.g.save_state(SC+'/play/k20.st')
