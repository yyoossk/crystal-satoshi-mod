import sys; sys.path.insert(0,'play'); from bot import *
b=Bot(state=SC+'/play/k10c.st', out=SC+'/play/run/k11')
r=b.travel('Route24'); print(r, b.where(), b.log[-5:])
b.cross('U'); print(b.where())
r=b.travel('Route25'); print(r, b.where(), b.log[-5:])
r=b.travel((26,51)); print('bill', r, b.where(), b.log[-5:])
b.g.save_state(SC+'/play/k11.st')
