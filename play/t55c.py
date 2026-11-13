import sys; sys.path.insert(0,'play'); from bot import *
g, x, y = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
b=Bot(state=SC+'/play/k10c.st', out=SC+'/play/run/t55_'+g)
b.ev(shots=False)
b.warp(g,x,y); b.wait(60)
b.face('U'); b.press('A',40); b.shot(); b.ev()
print(g, 'badges', b.peek(0xD84A,2), b.log)
b.face('U'); b.press('A',40); b.shot(); b.ev()
b.sheet('a',8)
