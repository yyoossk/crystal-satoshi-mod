import sys; sys.path.insert(0,'play'); from bot import *
b=Bot(state=SC+'/play/k25b.st', out=SC+'/play/run/k26')
for i in range(60):
    b.wait(120); b.press('A',30)
    if i%4==0: b.shot()
    k=b.peek(W_MAP,2)
print(b.where())
b.ev(); b.shot()
for i in range(10): b.wait(60); b.ev()
print(b.where(), b.objpos())
b.g.save_state(SC+'/play/k26.st')
