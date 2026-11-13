import sys; sys.path.insert(0,'play'); from bot import *
b=Bot(state=SC+'/play/k27.st', out=SC+'/play/run/k28')
b.warp((15,2),7,12); b.wait(60); b.ev()
b.goto(7,13) ; b.step('L'); b.step('R')
b.talk_to(6,11); b.ev()
print(b.where())
for i in range(30):
    b.wait(60); b.ev()
    if b.where()[0] not in [(15,2)]: break
print(b.where())
for i in range(40): b.wait(60); b.ev(); 
print(b.where())
b.g.save_state(SC+'/play/k28.st')
