import sys; sys.path.insert(0,'play'); from bot import *
b=Bot(state=SC+'/play/k25.st', out=SC+'/play/run/k25b')
print(b.objpos())
for i in range(4): b.step('U'); print(b.where()); b.ev()
b.talk_to(5,3) if (5,3) in b.objpos() else None
b.ev()
for i in range(100):
    b.press('A',60)
    if i%3==0: b.shot()
print(b.where())
b.g.save_state(SC+'/play/k25b.st')
