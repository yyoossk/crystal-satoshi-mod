import sys; sys.path.insert(0,'.')
from t64a import *
rom=sys.argv[1]; O=SC+'/run/t66/'+sys.argv[2]; import os; os.makedirs(O,exist_ok=True)
make_test_rom(SC+'/build/%s.gbc'%rom)
b=Bot(state='blogbase2.st', out=O)
b.script([0x5D, 72, 1, 0x5E, 0x5F], 30)
for i in range(70):
    b.wait(12); b.g.shot(O+'/a%02d.png'%i)
    if i>14 and i%3==0: b.press('A',10)
b.g.close()
