import sys; sys.path.insert(0,'play'); from bot import *
b=Bot(state=SC+'/play/k22.st', out=SC+'/play/run/k23d')
b.warp((26,35),7,11); b.wait(60); b.shot()
b.step('D'); b.ev(); print(b.where(), b.objpos())
b.g.save_state(SC+'/play/k23.st')
