import sys; sys.path.insert(0,'play'); from bot import *
b=Bot(state=SC+'/play/k18.st', out=SC+'/play/run/k19')
b.ev()
print(b.where(), b.objpos(), b.objs_of())
b.wait(100); print(b.objpos())
fuji=[o for o in b.objs_of() if o[0] in (9,0x2f,47)]
print(fuji)
for o in b.objpos():
    b.talk_to(*o)
b.g.save_state(SC+'/play/k19.st')
# Snorlax route 12
k=b.ids.get('Route12'); print(k, [ (o) for o in b.objs_of(k)][:20])
