import sys; sys.path.insert(0,'.')
from t64a import *
make_test_rom(SC+'/build/p65.gbc')
b=Bot(state='blogbase2.st', out='/tmp/x')
b.script([0x5D, 72, 1, 0x5E, 0x5F], 30)
b.wait(300)
def dump():
    b.bank1(); a=b.peek(0xcdcd,360)
    for r in range(18): print(''.join('%x'%v for v in a[r*20:r*20+20]))
dump()
b.g.close()
