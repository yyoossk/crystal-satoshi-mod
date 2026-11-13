import sys; sys.path.insert(0,'play')
from t64a import *
make_test_rom(SC+'/build/p71.gbc')
b=Bot(state=SC+'/play/blogbase2.st', out=SC+'/run/card')
b.wait(60)
for n in range(8):
    b.press('S',40)
    for j in range(n): b.press('D',12)
    b.press('A',80)
    b.shot('n%d'%n)
    for j in range(5): b.press('B',30)
