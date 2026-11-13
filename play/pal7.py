import sys; sys.path.insert(0,'play')
from t64a import *
ROM=sys.argv[1]
make_test_rom(SC+'/build/%s.gbc'%ROM)
b=Bot(state=SC+'/play/vir_%s.st'%ROM, out=SC+'/run/pal7')
for m,x,y in (('Route1',10,20),('PalletTown',10,5),('ViridianCity',21,20),('NewBarkTown',10,8),('Route29',30,10),('CherrygroveCity',10,8)):
    b.warp(m,x,y); b.wait(120); b.clear_text(); b.wait(60)
    p=b.g.pals(); bg=p.split()[0][3:]
    print(m, [bg[i*16:(i+1)*16] for i in range(8)])
