import sys; sys.path.insert(0,'.')
from bot import *
make_test_rom(sys.argv[1])
b=Bot(state='p64nb.st', out=SC+'/run/tbox2_'+sys.argv[2])
b.g.poke(0xDC9D,0); b.g.poke(0xDC9E,0xFF)
b.script([0x2D, 4, 24, 0, 0], 120); b.g.shot(SC+'/run/tbox2a_%s.png'%sys.argv[2])
for i in range(3): b.press('B',40)
b.script([0x2D, 25, 22, 0, 0], 120); b.g.shot(SC+'/run/tbox2b_%s.png'%sys.argv[2])
