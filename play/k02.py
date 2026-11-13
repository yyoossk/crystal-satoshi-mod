import sys; sys.path.insert(0,'play'); from bot import *
b=Bot(state=SC+'/play/k01.st', out=SC+'/play/run/k02')
for i in range(30):
    b.press('A',40); b.shot()
print(b.where())
b.g.save_state(SC+'/play/k02.st')
b.sheet('a')
