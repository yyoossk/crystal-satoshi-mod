from t57b import act, act2, party, INV
from t57 import *
make_test_rom(SC + '/build/p60.gbc')
b = Bot(state='postjhof2.st', out=SC + '/run/t60')
b.g.poke(0xDC9D, 1); b.clrev(0x4F)
act(b, (11, 6), 2, 4, 'U', 'bill'); act2(b, 'bill'); print('bill', party(b), flush=True)
import build_phase57 as P
for k, cave, tod in (((24, 3), False, 1), ((10, 1), False, 2), ((3, 7), True, 1), ((24, 1), False, 0)):
    print(k, tod, sample(b, k, n=10, cave=cave, tod=tod), flush=True)
