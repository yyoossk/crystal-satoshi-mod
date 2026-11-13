from mlib import *
b=Bot(state=SC+'/play/mb1.st', out=SC+'/play/run/m3j')
sw(b,18,25); b.refresh_grid()
print('sw (20,3)', b.path(20,4) is not None)
sw(b,20,3); b.refresh_grid()
for o in [(10,2),(5,4),(5,13)]: print(' ball',o,near(b,o))
r=b.talk_to(5,13); b.ev(); print('talk', r, b.log[-2:]); b.shot('key')
b.g.save_state(SC+'/play/mkey.st')
