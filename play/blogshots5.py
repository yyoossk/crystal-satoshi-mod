import sys; sys.path.insert(0,'.')
from t64a import *
make_test_rom(SC+'/build/p65.gbc')
O=SC+'/run/blog/orig3'; import os; os.makedirs(O,exist_ok=True)
def S(b,n): b.g.shot(O+'/'+n+'.png')
b=Bot(sav=SC+'/play/p64nb.sav', out=O+'/y')
b.wait(600); b.press('S',80); S(b,'t'); b.press('A',120); S(b,'menu')
b.g.down('D'); b.wait(4); b.g.up('D'); b.wait(40); S(b,'menuD')
b.press('A',150)
for i in range(45):
    b.g.press('A',6,70); S(b,'oak%02d'%i)
