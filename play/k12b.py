import sys; sys.path.insert(0,'play'); from bot import *
b=Bot(state=SC+'/play/k12.st', out=SC+'/play/run/k12b')
b.goto(1,5); b.face('U'); b.press('A',40); b.shot(); b.ev()
b.wait(200); b.shot(); print(b.where(), b.objpos())
for i in range(4): b.wait(100); b.shot()
print(b.objpos())
# talk to Bill now
ob=b.objpos()
if ob: b.talk_to(*ob[0])
b.g.save_state(SC+'/play/k12b.st')
b.sheet('a',8)
