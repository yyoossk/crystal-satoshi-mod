import sys; sys.path.insert(0,'play'); from bot import *
b=Bot(state=SC+'/play/k11.st', out=SC+'/play/run/k12')
b.ev(shots=False)
b.warp((26,51),3,5); b.wait(60); print(b.where(), b.objs_of())
for o in b.objs_of():
    print('talk', o); b.talk_to(o[1],o[2])
    # Bill: answer yes, then use PC
for i in range(3):
    print(b.where(), b.objpos(), b.objs_of())
b.g.save_state(SC+'/play/k12.st')
b.sheet('a',8)
