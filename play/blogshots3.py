import sys; sys.path.insert(0,'.')
from t64a import *
make_test_rom(SC+'/build/p65.gbc')
O=SC+'/run/blog/orig'; import os; os.makedirs(O,exist_ok=True)
def S(b,n): b.g.shot(O+'/'+n+'.png')
# Jessie & James battle
b=Bot(state='blogbase2.st', out=O+'/x')
b.script([0x5D, 72, 1, 0x5E, 0x5F], 30)
for i in range(16):
    b.wait(15); S(b,'jj%02d'%i)
b.g.close()
# new game
b=Bot(sav=SC+'/play/p64nb.sav', out=O+'/y')
b.wait(500)
for i in range(3): b.press('A',80)
b.wait(60); S(b,'menu0')
b.g.press('D',8,40); S(b,'menu1'); b.g.press('A',8,120)
for i in range(40):
    b.g.press('A',6,60); S(b,'oak%02d'%i)
