import sys; sys.path.insert(0,'.')
from t64a import *
make_test_rom(SC+'/build/p65.gbc')
O=SC+'/run/blog/orig2'; import os; os.makedirs(O,exist_ok=True)
def S(b,n): b.g.shot(O+'/'+n+'.png')
b=Bot(state='blogbase2.st', out=O+'/x')
b.script([0x5D, 72, 1, 0x5E, 0x5F], 30)
for i in range(30):
    b.wait(20); S(b,'jj%02d'%i)
    if i>14 and i%3==0: b.press('A',10)
b.g.close()
b=Bot(sav=SC+'/play/p64nb.sav', out=O+'/y')
b.wait(500)
for i in range(3): b.press('A',80)
b.wait(120)
for t in range(5):
    b.g.down('D'); b.wait(3); b.g.up('D'); b.wait(30); S(b,'menu%d'%t)
    if b.has('さいしょから') and False: break
