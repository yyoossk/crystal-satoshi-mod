import sys; sys.path.insert(0,'play'); from bot import *
b=Bot(state=SC+'/play/k15.st', out=SC+'/play/run/k16')
print(b.objs_of((26,24)))
gio=[o for o in b.objs_of((26,24))][0]
b.warp((26,24), gio[1], gio[2]+2); b.wait(60); b.shot()
b.talk_to(gio[1], gio[2]); b.ev()
print(b.objpos(), b.log[-3:])
# pick up the scope (item ball after Giovanni leaves)
for o in b.objs_of((26,24)):
    print(o)
b.g.save_state(SC+'/play/k16.st')
b.sheet('a',8)
