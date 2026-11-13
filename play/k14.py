import sys; sys.path.insert(0,'play'); from bot import *
b=Bot(state=SC+'/play/k14c.st', out=SC+'/play/run/k14d')
b.g.poke(0xD83F, b.peek(0xD83F)[0]|4)
b.warp((26,148),21,20); b.wait(60)
print(b.plan('LavenderTown'))
r=b.travel('LavenderTown'); print('lavender', r, b.where(), b.log[-4:])
b.g.save_state(SC+'/play/k14d.st')
