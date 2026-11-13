import sys; sys.path.insert(0,'play'); from bot import *
b=Bot(state=SC+'/play/k17.st', out=SC+'/play/run/k18')
b.warp((26,19),11,15); b.wait(60); b.shot()
print(b.goto(10,16), b.where()); b.ev()
print(b.where())
b.go_warp((26,20)); b.ev(); print(b.where())
for o in b.objs_of():
    print('talk', o); b.talk_to(o[1], o[2])
print(b.where(), b.log[-3:])
b.g.save_state(SC+'/play/k18.st')
