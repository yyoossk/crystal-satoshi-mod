import sys; sys.path.insert(0,'play'); from bot import *
b=Bot(state=SC+'/play/dock.st', out=SC+'/play/run/chk6')
print(b.where(), b.textbox(), b.pc())
b.shot()
b.g.down('R'); b.wait(30); b.g.up('R'); b.wait(90); print(b.where()); b.shot()
b.step('L'); b.step('R'); b.g.down('R'); b.wait(30); b.g.up('R'); b.wait(90); print(b.where()); b.shot()
