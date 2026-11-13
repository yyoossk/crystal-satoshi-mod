import sys; sys.path.insert(0,'play'); from soko import *
b=Bot(state=SC+'/play/k21.st', out=SC+'/play/run/mdbg')
b.warp((26,57),14,10); b.wait(60); b.shot('a'); print(b.where())
b.step('U'); b.wait(10); print(b.where()); b.step('U'); b.wait(10); print(b.where()); b.shot('b')
b.warp((26,57),13,14); b.wait(60); b.step('D'); b.wait(10); print(b.where()); b.shot('c')
