import sys; sys.path.insert(0,'play'); from bot import *
b=Bot(state=SC+'/play/k16.st', out=SC+'/play/run/k17')
b.talk_to(25,2); print('scope?', b.log[-2:])
b.warp('LavenderTown',14,6); b.wait(40); b.ev()
k=b.ids['LavenderTown']; print(b.db.warps(k))
r=b.travel((26,14)); print('tower1', r, b.where())
r=b.travel((26,20)); print('tower7', r, b.where(), b.log[-4:])
b.g.save_state(SC+'/play/k17.st')
