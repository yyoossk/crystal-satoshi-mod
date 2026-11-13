import sys; sys.path.insert(0,'play'); from bot import *
b=Bot(state=SC+'/play/k21.st', out=SC+'/play/run/k22b')
b.ev(shots=False)
b.warp((26,31),5,3); b.wait(60)
b.step('L'); 
for i in range(10): b.wait(8); b.shot()
print(b.where())
b.step('L')
for i in range(30): b.wait(8); b.shot()
