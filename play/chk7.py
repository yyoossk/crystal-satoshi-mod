import sys; sys.path.insert(0,'play'); from bot import *
b=Bot(state=SC+'/play/dock3.st', out=SC+'/play/run/chk7')
b.step('D'); b.wait(60); b.step('U'); b.wait(100); print(b.where()); b.shot()
for d in 'DDDD':
    print(d, b.step(d), b.where()); b.wait(60); b.shot()
print(b.where())
