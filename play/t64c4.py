import sys
from t64c import *
make_test_rom(sys.argv[1])
b=Bot(state='p64nb.st', out=OUT+'/catchb_'+sys.argv[2])
b.giveitem(0x05, 30); setlast(b, 0x05)
b.script([0x5C, 0x8F, 100, 0x5E, 0x5F], 30)
for i in range(60): b.wait(10)
b.press('A',30); b.wait(300)
for k in range(4):
    b.g.press('s',6,30); b.wait(30); b.shot('s%d'%k)
    for j in range(10):
        b.g.press('B',4,40)
    b.wait(120); b.shot('m%d'%k)
strip(b.out,'s')
