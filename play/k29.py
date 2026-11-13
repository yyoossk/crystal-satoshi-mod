import sys; sys.path.insert(0,'play'); from bot import *
b=Bot(state=SC+'/play/k28.st', out=SC+'/play/run/k29')
b.warp((15,5),6,2); b.wait(60); b.shot()
b.face('R'); b.press('A',40); b.shot(); b.ev()
for i in range(20): b.wait(60); b.ev()
print(b.where())
b.go_warp((15,3)) if b.where()[0]==(15,5) else None
for i in range(20): b.wait(60); b.ev()
print(b.where())
b.g.save_state(SC+'/play/k29.st')
