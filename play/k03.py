import sys; sys.path.insert(0,'play'); from bot import *
b=Bot(state=SC+'/play/k02.st', out=SC+'/play/run/k03')
b.clear_text()
print(b.where(), b.goto(6,5)); b.face('U'); b.shot()
for i in range(25):
    b.press('A',40); b.shot()
print(b.where(), b.peek(0xDC9E,7))
b.g.save_state(SC+'/play/k03.st')
b.sheet('a')
