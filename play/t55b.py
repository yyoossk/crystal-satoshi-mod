import sys; sys.path.insert(0,'play'); from bot import *
b=Bot(state=SC+'/play/k08.st', out=SC+'/play/run/t55b')
b.ev(shots=False)
b.warp('FuchsiaGym',1,11); b.wait(60); b.shot('in'); print(b.objpos())
b.face('U'); b.press('A',40); b.shot(); b.ev()
print('badge', b.peek(0xD84A,2), b.log)
b.sheet('a',8)
