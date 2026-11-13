import sys; sys.path.insert(0,'play'); from bot import *
b=Bot(state=SC+'/play/k06.st', out=SC+'/play/run/k07')
b.ev(shots=False)
b.go_warp('PalletTown'); b.shot()
b.cross('U'); b.shot(); b.cross('U'); b.shot(); b.cross('U'); b.shot()
print(b.where())
for d in [(26,83),(26,84),(26,85)]:
    print(b.go_warp(d), b.where()); b.shot()
print(b.go_warp('Route2'), b.where()); b.shot()
b.cross('U'); b.shot(); print(b.where(), b.log)
b.g.save_state(SC+'/play/k07.st')
b.sheet('a',8)
