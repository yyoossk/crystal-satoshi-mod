import sys; sys.path.insert(0,'.')
from t64a import *
make_test_rom(SC+'/build/p66.gbc')
b=Bot(state='blogbase2.st', out='/tmp/x')
b.script([0x5D, 72, 1, 0x5E, 0x5F], 30)
b.wait(300)
for i in range(16): b.press('A',20)
b.wait(100)
b.bank1()
m=bytes(b.peek(0xc000,0x2000))
import re
b.g.shot(SC+'/run/t66/s.png'); print(bytes(b.peek(0xd200,0x80)).hex(' ')); print([hex(0xc000+x.start()) for x in re.finditer(b'\x00\x24',m)][:40])
b.g.close()
