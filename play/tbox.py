import sys; sys.path.insert(0,'.')
from bot import *
make_test_rom(sys.argv[1])
b=Bot(state='postjhof2.st', out=SC+'/run/tbox_'+sys.argv[2])
b.warp((24,4),10,8); b.wait(80)
for i in range(25): b.press('A',40)
b.script([0x2D, 25, 5, 0, 0], 120); b.g.shot(SC+'/run/tbox_%s.png'%sys.argv[2])
