import sys; sys.path.insert(0,'play'); from bot import *
b=Bot(state=SC+'/play/k05.st', out=SC+'/play/run/k06')
b.clear_text(shots=False)
b.warp_near('PalletTown',12,12); b.shot()
b.step('U'); b.wait(80); print(b.where(), b.objpos())
b.goto(4,3) or b.goto(5,3); b.face('U'); b.shot()   # Oak
b.press('A',40); b.ev()
print(b.where(), 'dex flag?', b.peek(0xD957,4))
b.g.save_state(SC+'/play/k06.st')
b.sheet('a',8)
