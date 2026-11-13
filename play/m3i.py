from mlib import *
b=Bot(state=SC+'/play/mb1.st', out=SC+'/play/run/m3i')
b.refresh_grid()
for s in [(20,3),(18,25)]: print('switch',s, b.path(s[0],s[1]+1) is not None)
s=[s for s in [(20,3),(18,25)] if b.path(s[0],s[1]+1) is not None][0]
sw(b,*s); print('after', reach(b))
for o in [(10,2),(5,4),(5,13)]: print(' ball',o,near(b,o))
r=b.talk_to(5,13); b.ev(); print('talk', r, b.log[-2:]); b.shot('key')
b.g.save_state(SC+'/play/mkey.st')
