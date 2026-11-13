import sys; sys.path.insert(0,'.')
from t64a import *
make_test_rom(SC+'/build/'+sys.argv[1]+'.gbc')
O=SC+'/run/rst_'+sys.argv[1]; import os; os.makedirs(O,exist_ok=True)
b=Bot(sav=SC+'/play/p64nb.sav', out=O)
b.wait(600); b.press('S',80); b.press('A',120)
b.g.down('D'); b.wait(4); b.g.up('D'); b.wait(40)
b.press('A',150)
for i in range(45):
    b.g.press('A',6,70); b.g.shot(O+'/%02d.png'%i)
    print(i, b.pc(), flush=True)
