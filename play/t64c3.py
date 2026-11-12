import sys
from t64c2 import *
make_test_rom(sys.argv[1])
b=Bot(state='p64nb.st', out=OUT+'/catch_'+sys.argv[2])
print(trial3(b,0x8F,100,0x05,0,tag='sn',maxthrow=4))
strip(b.out,'s')
