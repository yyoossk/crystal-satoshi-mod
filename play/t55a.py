import sys; sys.path.insert(0,'play'); from bot import *
b=Bot(state=SC+'/play/k07.st', out=SC+'/play/run/t55a')
b.ev(shots=False)
b.warp('PewterGym',5,2); b.wait(60)
b.face('U'); b.press('A',40); b.shot(); b.ev()
print('badge', b.peek(0xD84A,2), b.log)
# talk again
b.face('U'); b.press('A',40); b.shot(); b.ev()
# guide
b.goto(6,12); b.face('U'); b.press('A',40); b.shot(); b.ev()
b.sheet('a',8)
# item check: TM34 in bag?
