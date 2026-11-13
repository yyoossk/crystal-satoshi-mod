import sys; sys.path.insert(0,'play'); from bot import *
b=Bot(state=SC+'/play/k10b.st', out=SC+'/play/run/k10c')
r=b.travel('CeruleanCity'); print(r, b.where(), b.log[-5:])
b.g.save_state(SC+'/play/k10c.st')
