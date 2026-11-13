import sys; sys.path.insert(0,'play'); from bot import *
b=Bot(state=SC+'/play/k23.st', out=SC+'/play/run/k23e')
for i in range(6): b.wait(60); b.shot(); b.ev()
print(b.where(), b.objpos(), b.in_battle())
b.g.save_state(SC+'/play/k23e.st')
