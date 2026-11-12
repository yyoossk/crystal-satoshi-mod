from t57b import act, act2, party, INV
from t57 import *
make_test_rom(SC + '/build/p58.gbc')
b = Bot(state='postjhof2.st', out=SC + '/run/t58b')
act(b, (26, 73), 1, 5, 'U', 'odd'); act2(b, 'odd')
b.g.cmd('wait 1')
# Jenny before the Thunder Badge: clear engine flag 0x25 (clearflag)
b.script([0x35, 0x25, 0x00], 30)
act(b, (12, 3), 19, 16, 'U', 'jen0'); act2(b, 'jen0'); print(party(b))
