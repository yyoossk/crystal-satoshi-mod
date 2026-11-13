import sys; sys.path.insert(0,'.')
from t57 import *
make_test_rom(sys.argv[1])
b=Bot(sav=SC+'/play/p64nb.sav', out=SC+'/run/dc_'+sys.argv[2])
b.wait(400)
for i in range(3): b.press('A',60)
for i in range(8): b.press('A',90)
b.wait(120); set_tod(b,1); b.warp((24,4),10,9); b.wait(100); b.step('D'); b.wait(30)
b.g.shot(SC+'/run/day_%s.png'%sys.argv[2])
