import sys; sys.path.insert(0,'play'); from bot import *
b=Bot(state=SC+'/play/dock.st', out=SC+'/play/run/chk5e')
print(b.db.warps((26,41)))
b.warp((26,41),26,1); b.wait(60); b.shot()
b.g.down('U'); b.wait(30); b.g.up('U'); b.wait(120); print(b.where()); b.shot()
for i in range(20): b.wait(60); b.ev(); b.shot()
print(b.where())

b.g.save_state(SC+'/play/dock3.st')
b.step('D'); b.wait(100); print('to dock', b.where()); b.shot()
for d in 'UUUUUU':
    b.step(d); print(d, b.where())
b.wait(100); print(b.where()); b.shot()
