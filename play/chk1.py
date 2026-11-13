import sys; sys.path.insert(0,'play'); from bot import *
b=Bot(state=SC+'/play/k27.st', out=SC+'/play/run/chk1')
b.warp('LavenderTown',3,8); b.wait(60)
for d in 'UUU': print(d, b.step(d), b.where()); b.wait(60); print(b.where())
G=grid_of(b.db.r,b.db.maps[(18,4)]['hdr']); print([hex(G[y][3]) for y in range(3,9)])
b2=Bot(state=SC+'/play/k16.st', rom=SC+'/build/test_play.gbc', out=SC+'/play/run/chk1b')
b2.warp('LavenderTown',3,8); b2.wait(60)
for d in 'UUU': print('pre', d, b2.step(d), b2.where()); b2.wait(60); print(b2.where())
