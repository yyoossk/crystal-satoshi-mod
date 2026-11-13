import sys; sys.path.insert(0,'play')
from t64a import *
make_test_rom(SC+'/build/p69.gbc')
b=Bot(state=SC+'/play/n1.st', out=SC+'/run/n2')
for i in range(30):
    if b.textbox(): b.press('A',30)
    else: b.wait(20)
print(b.shot(), b.where(), b.objs_of())
b.g.save_state(SC+'/play/n2.st')
