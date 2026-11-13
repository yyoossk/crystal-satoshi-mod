import sys; sys.path.insert(0,'play'); from bot import *
b=Bot(state=SC+'/play/k26.st', out=SC+'/play/run/k27')
b.go_warp('OaksLab'); b.wait(60); b.ev(); print(b.where(), b.objpos())
for o in b.objs_of():
    if o[0]==5: b.talk_to(o[1],o[2])
b.ev()
print(b.where(), b.log[-2:])
b.g.save_state(SC+'/play/k27.st')
