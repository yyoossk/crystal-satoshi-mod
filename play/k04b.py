import sys; sys.path.insert(0,'play'); from bot import *
b=Bot(state=SC+'/play/k04.st', out=SC+'/play/run/k04b')
b.battle(); b.shot('after'); b.clear_text(); b.shot('after2')
print(b.where(), b.peek(0xDC9D,8))
b.g.save_state(SC+'/play/k04b.st')
b.sheet('a',8)
