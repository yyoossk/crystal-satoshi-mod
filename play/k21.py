import sys; sys.path.insert(0,'play'); from bot import *
b=Bot(state=SC+'/play/k20.st', out=SC+'/play/run/k21')
b.ev(shots=False)
# Safari gate: pay & enter
k=b.ids['FuchsiaCity']; print([w for w in b.db.warps(k)])
w=[w for w in b.db.warps(k) if (w[3],w[4])==(26,87)][0]
b.warp(k,w[0],w[1]+1); b.wait(40); b.ev()
b.go_warp((26,87)); b.wait(60); b.ev(); print(b.where())
r=b.travel((26,88)); print('center', r, b.where())
b.ev()
b.g.save_state(SC+'/play/k21a.st')
# secret house
b.warp((26,96),3,5); b.wait(60)
for o in b.objs_of(): b.talk_to(o[1],o[2])
b.g.save_state(SC+'/play/k21.st')
